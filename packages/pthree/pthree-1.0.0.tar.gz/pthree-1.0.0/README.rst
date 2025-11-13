pthree: Python Project Parser
=============================

**A simple project parser for Python.**

This package is designed to be a lightweight, dependency-free tool for parsing project trees using python's
built-in ``ast``, ``importlib``, and ``inspect`` modules. It was originally developed as a series of
helper functions used to generate ASTs which could be passed to Sphinx's ``sphinx.ext.autosummary`` extension;
I have since extracted it into its own package for easier reuse *viz.* so that it can be injected into other
documentation projects.

Installation
------------
You can install the package directly from PyPI using pip:

.. code-block:: bash

    pip install pthree

Examples
--------
Here is a simple example demonstrating how to use the package to parse a project tree:

.. code-block:: python

    import json
    from pthree import build_node_tree, node_tree_to_dict


    node_tree = build_node_tree(json)
    node_dict = node_tree_to_dict(node_tree)

    print(json.dumps(node_dict, indent=2, sort_keys=False, ensure_ascii=False))
