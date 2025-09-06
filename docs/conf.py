'''Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

-- Project information -----------------------------------------------------
https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
'''

# ----------------------------------------------------------------------------
''' Sphinx source files path setup

If extensions (or modules to document with autodoc) are in another directory,
  add these directories to sys.path here. If the directory is relative to the
  documentation root, use os.path.abspath to make it absolute, like shown here.
'''

import os
import sys
import django

sys.path.insert(0, os.path.abspath("../"))
# sys.path.insert(0, os.path.abspath("./"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthy_meals.settings")
django.setup()

project = 'Healthy Meals Diet Assistant'
copyright = '2025, AGPL-3.0-only, David A. Taylor @ Taylored Web Sites'
author = 'David A. Taylor @ Taylored Web Sites'

# ----------------------------------------------------------------------------
''' Sphinx General configuration'''

''' Sphinx extensions

Add any Sphinx extension module names here, as strings. They can be extensions
   coming with Sphinx (named 'sphinx.ext.*') or your custom ones.

'''
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon", # https://sphinxcontrib-napoleon.readthedocs.io/en/latest/
    "sphinx.ext.intersphinx", # provides links to other .rst files
    "sphinx.ext.viewcode",
    "sphinxcontrib_django", # https://pypi.org/project/sphinxcontrib-django/
    "sphinx_mdinclude", # https://pypi.org/project/sphinx_mdinclude/
    "sphinx.ext.todo", # see: https://www.sphinx-doc.org/en/master/usage/extensions/todo.htm
]

# https://github.com/sphinx-doc/sphinx/issues/825#issuecomment-180197293
source_parsers = {
    '.md': 'recommonmark.parser.CommonMarkParser',
}
source_suffix = ['.rst', '.md']

'''Configure the path to the Django settings module'''
django_settings = "healthy_meals.settings"

'''Options for HTML output

https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
https://pypi.org/project/sphinx-rtd-theme/

'''
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['css/custom.css'] # custom css for full width pages

'''Other settings'''
templates_path = ['_templates']
exclude_patterns = ["**/healthy_meals"]
autosummary_generate = True
# Include the database table names of Django models
django_show_db_tables = True                # Boolean, default: False
# Add abstract database tables names (only takes effect if django_show_db_tables is True)
django_show_db_tables_abstract = True       # Boolean, default: False
todo_include_todos = True   # see: https://www.sphinx-doc.org/en/master/usage/extensions/todo.htm
# todo_emit_warnings = False   # see: https://github.com/sphinx-doc/sphinx/issues/2680
