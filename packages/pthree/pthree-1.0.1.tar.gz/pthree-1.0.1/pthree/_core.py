"""
Core logic for building a JSON-ish AST representation of a Python project.

This module was inspired by the need to generate structured representations of Python
projects for documentation purposes. It leverages Python's introspection capabilities to
classify and organize project members into a hierarchical tree structure.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import pkgutil
import re
from dataclasses import dataclass, field, asdict
from types import ModuleType, MappingProxyType
from typing import Iterable, List

__all__ = ["build_node_tree",
           "node_tree_to_dict",
           "Node",
           "PACKAGE_ORDERING"]


_MEMBER_TYPES = (
    "package",
    "module",
    "class",
    "exception",
    "method",
    "class_method",
    "static_method",
    "property",
    "data",
    "function",
    "attribute",
    "descriptor"
)
"""Tuple of member type strings for deterministic ordering."""


PACKAGE_ORDERING = MappingProxyType({k: i for i, k in enumerate(_MEMBER_TYPES)})
"""Mapping of member type to its ordering index."""


@dataclass(slots=True)
class Node:
    """
    Simple dataclass to categorize members of a project AST.

    Attributes
    ----------
    name : int
        Node name
    kind : int
        Node kind
    children : list[Node]
        Child nodes
    """
    name: str
    kind: str
    children: List[Node] = field(default_factory=list)


def build_node_tree(root: str | ModuleType,
                    sort_children: bool = False,
                    exclude_private: bool = False,
                    exclude_tests: bool = False,
                    exclude_dunder: bool = False,
                    exclusions: Iterable[str] | None = None
                    ) -> Node:
    """
    Build a JSON-ish API tree suitable for Jinja templating.

    Parameters
    ----------
    root : str | ModuleType
        A package or module object, or its importable dotted name.
    sort_children : bool
        Whether to sort child nodes by kind and name.
    exclude_private : bool
        Whether to exclude private members (names starting with a single underscore).
    exclude_tests : bool
        Whether to exclude test modules (names containing 'test' or 'tests').
    exclude_dunder : bool
        Whether to exclude dunder members (names surrounded by double underscores).
    exclusions : Iterable[str] | None
        Additional regex patterns to exclude members by their fully-qualified names.

    Returns
    -------
    Node
        The root node of the built tree.
    """
    base_exclusions = _generate_base_exclusions(exclude_private, exclude_tests, exclude_dunder)
    exclusions = exclusions or []
    exclusions.extend(base_exclusions)

    mod = importlib.import_module(root) if isinstance(root, str) else root
    node = _module_to_node(mod, sort_children=sort_children, exclude=exclusions)
    return node


def node_tree_to_dict(node: Node) -> dict:
    """
    Convert a Node tree to a dictionary suitable for JSON serialization.
    """
    return asdict(node)


def _generate_base_exclusions(private: bool,
                             tests: bool,
                             dunder: bool) -> list[str]:
    patterns = []
    if private:
        patterns.append("(?:^|\\.)_[^.]+(?:\\.|$)")
    if tests:
        patterns.append("(?:^|\\.)(?:tests?|test_[^.]+|[^.]+_test)(?:\\.|$)")
    if dunder:
        patterns.append("(?:^|\\.)__[^.]+__(?:\\.|$)")
    return patterns


def _check_exclusions(name, patterns):
    for pattern in patterns:
        if re.search(pattern, name):
            return True
    return False


def _is_package(module: ModuleType) -> bool:
    return hasattr(module, "__path__")


def _fqn_for_class_member(owner: type, name: str, obj: object | None = None) -> str:
    """
    Build a fully-qualified dotted name for an attribute on `owner`.
    Prefer the owner's module/qualname; fall back to the object's module.
    """
    mod = getattr(owner, "__module__", None) or getattr(obj, "__module__", None) or "builtins"
    qual = getattr(owner, "__qualname__", getattr(owner, "__name__", ""))
    return f"{mod}.{qual}.{name}"


def _fqn_for_module_member(module: ModuleType, name: str, value: object) -> str:
    """Fully qualified dotted name for a member of `module`."""
    if inspect.isclass(value) or inspect.isfunction(value):
        mod = getattr(value, "__module__", module.__name__) or module.__name__
        qual = getattr(value, "__qualname__", getattr(value, "__name__", name))
        return f"{mod}.{qual}"
    # everything else: data/consts/enums instances, etc.
    return f"{module.__name__}.{name}"



def _iter_immediate_children(module: ModuleType) -> Iterable[tuple[str, bool]]:
    """
    Yield (child_name, is_pkg) for *immediate* children only.

    Uses pkgutil.iter_modules over module.__path__ if package; otherwise yields none.
    """
    if not _is_package(module):
        return []
    for mi in pkgutil.iter_modules(module.__path__):  # immediate only
        yield mi.name, mi.ispkg


def _defined_and_imported_names_via_ast(module: ModuleType) -> tuple[set[str], set[str]]:
    """
    Return (defined_names, imported_names) at module top level using AST.

    - defined_names: names assigned/annotated/aug-assigned, as well as class/def names
    - imported_names: direct names bound by 'import' and 'from ... import ...'

    If source is unavailable (C extensions, builtins), both sets may be empty.
    """
    src = None
    defined: set[str] = set()
    imported: set[str] = set()

    try:
        src = inspect.getsource(module)
    except:
        filename = getattr(module, "__file__", None)
        if filename and filename.endswith(".py"):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    src = f.read()
            except:
                pass

    try:
        tree = ast.parse(src)
    except:
        return defined, imported

    for node in tree.body:  # only top-level
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                defined |= _collect_assigned_names(tgt)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            defined |= _collect_assigned_names(node.target)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            # from .x import a as b
            for alias in node.names:
                if alias.name == "*":
                    # Can't know; skip (treat as neither defined nor imported here)
                    continue
                imported.add(alias.asname or alias.name)

    return defined, imported


def _collect_assigned_names(target: ast.AST) -> set[str]:
    out: set[str] = set()
    if isinstance(target, ast.Name):
        out.add(target.id)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            out |= _collect_assigned_names(elt)
    # ignore attributes/subscripts; they don't bind module names
    return out


def _class_to_children(cls: type, /, sort_children: bool, exclude: Iterable) -> list[Node]:
    """
    Classify class members using inspect.classify_class_attrs, following the user's
    original filters:
      - skip dunder names
      - only include members whose defining_class is the class itself

    Kinds are mapped to:
      'method', 'class_method', 'static_method', 'property', 'data'
    """
    children: list[Node] = []
    try:
        members = inspect.classify_class_attrs(cls)
    except:
        return children

    for m in members:
        if m.defining_class is cls:
            fqn = _fqn_for_class_member(cls, m.name, m.object)
            if _check_exclusions(fqn, exclude):
                continue
            children.append(Node(m.name, m.kind.replace(" ", "_")))

    if sort_children:
        children.sort(key=lambda d: (PACKAGE_ORDERING.get(d.kind, 99), d.name))
    return children


def _module_to_node(module: ModuleType, /, sort_children: bool, exclude: Iterable) -> Node:
    """
    Convert a module/package object to a {name, kind, children} node.
    """
    if _check_exclusions(module.__name__, exclude):
        raise ValueError(f"Root module ``{module.__name__}`` is excluded")
    name = module.__name__.split(".")[-1]
    children: list[Node] = []
    kind = "package" if _is_package(module) else "module"

    # Subpackages / submodules (immediate)
    if kind == "package":
        for child_name, is_pkg in _iter_immediate_children(module):
            fqn = f"{module.__name__}.{child_name}"
            try:
                child_mod = importlib.import_module(fqn)
            except Exception:
                # Skip broken/optional imports
                continue
            if _check_exclusions(fqn, exclude):
                continue
            children.append(_module_to_node(child_mod, sort_children, exclude))

    # Functions / Classes / Exceptions (module-defined only)
    for member_name, value in inspect.getmembers(module):
        vmod = inspect.getmodule(value)

        # CLASSES (incl. exceptions)
        if inspect.isclass(value) and vmod is module:
            fqn = _fqn_for_module_member(module, member_name, value)
            if _check_exclusions(fqn, exclude):
                continue
            cls_children = _class_to_children(value, sort_children, exclude)
            if issubclass(value, Exception):
                children.append(Node(member_name, "exception", cls_children))
            else:
                children.append(Node(member_name, "class", cls_children))

        # FUNCTIONS
        elif inspect.isfunction(value) and vmod is module:
            fqn = _fqn_for_module_member(module, member_name, value)
            if _check_exclusions(fqn, exclude):
                continue
            children.append(Node(member_name, "function"))

    # ATTRIBUTES (data) — top-level assigned names that aren't functions/classes/modules
    # Use module dict to read current values, but gate by AST-defined names and not imported
    # Members defined in this module (exclude imports)
    defined_names, imported_names = _defined_and_imported_names_via_ast(module)
    for member_name in defined_names - imported_names:
        if hasattr(module, member_name):
            value = getattr(module, member_name)
            if not inspect.ismodule(value) and not inspect.isclass(value) and not inspect.isfunction(value):
                fqn = _fqn_for_module_member(module, member_name, value)
                if _check_exclusions(fqn, exclude):
                    continue
                children.append(Node(member_name, "attribute"))

    # Deterministic child ordering (optional)
    if sort_children:
        children.sort(key=lambda d: (PACKAGE_ORDERING.get(d.kind, 99), d.name))

    return Node(name, kind, children)
