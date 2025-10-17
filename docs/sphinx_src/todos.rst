To Do Lists
===========


How "todo" items get into sphinx docs
=====================================

1. conf.py configuration (docs/conf.py)

  .. code-block:: python

    extensions = [
        "sphinx.ext.autodoc", # to get items from docstrings
        ...
        "sphinx.ext.todo", # see: https://www.sphinx-doc.org/en/master/usage/extensions/todo.htm
    ]
    todo_include_todos = True   # see: https://www.sphinx-doc.org/en/master/usage/extensions/todo.htm

|

****


How to enter a "todo" item into .rst (reStructuredText) files
=============================================================

If a .rst file has the following code:

.. code-block:: rst

    Example To Do List:

    .. ToDo:: Example single row todo item

    .. ToDo:: Example labeled bulleted todo list:

       - Example Item 1
       - Example Item 2

.. Uncomment me if you want to temporarily see what it will look like (after rebuild)
.. Then it will look like this in the Sphinx documentation:

.. .. ToDo:: Example single row todo item

.. .. ToDo:: Example labeled bulleted todo list:

..     - Example Item 1
..     - Example Item 2

|

====


How to enter "todo" items into code documentation (in docstrings)
=================================================================

If python has the following docstring:

.. code-block:: text

    '''Example "todo" items in a python docstring style comment

    .. ToDo:: Example single row todo item

    .. ToDo:: Example labeled bulleted todo list:

        - Example Item 1
        - Example Item 2
    '''

.. Uncomment me if you want to temporarily see what it will look like (after rebuild)
.. It will similarly look like the following in Sphinx Documentation:

.. .. ToDo:: Example single row todo item

.. .. ToDo:: Example labeled bulleted todo list:

..     - Example Item 1
..     - Example Item 2

.. Note: it will also be displayed in the appropriate place in the python code documentation

|

----


Current To Do items Listings (combined from all docs):
=============================

.. todolist::
