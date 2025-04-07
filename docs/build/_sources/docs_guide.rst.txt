Documentation Guide
===================


Code Documentation Philosophy
-----------------------------

The philosophy of documentation in the Healthy Meals project is to have the documentation be part of what is being documented (aka: `Docs as Code <https://www.writethedocs.org/guide/docs-as-code/>`_).

The choice to use the google style documentation was motivated by an sphinx article on `napoleon legible docstrings <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/#google-vs-numpy>`_.  It is recommended to use one style through out a project, and the `google style <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_ seems to be more popular, especially for non-scientific applications.

Using docstrings for code documentation:

- `Google Style Python Docstrings <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_.
- `Describing code in Sphinx <https://www.sphinx-doc.org/en/master/tutorial/describing-code.html>`_.


Code Documentation Process Overview
-----------------------------------

Code is being documented using the `Sphinx <https://www.sphinx-doc.org/>`_ toolset, which is the defacto standard tool for documenting django/python.  The Sphinx toolset recognizes `NumPy <https://numpy.org/doc/stable/>`_ , `Google <https://google.github.io/styleguide/pyguide.html>`_ , and `rst <https://peps.python.org/pep-0287/>`_ code documentation standards.  This is achieved by using the `Napoleon <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/>`_ extension to Sphinx.  When code has docstrings appropriately placed within it, Sphinx will automatically pull them into the documentation in the docs directory.  The healthy-meals github repository has been set up to automatically deliver the documentation to a `github pages site on the internet <https://tayloredwebsites.github.io/healthy-meals/build/index.html>`_.


Generation of the Documentation.
----------------------------------

`nox <https://nox.thea.codes/en/stable/tutorial.html>`_ is the automation tool we use generate or update the documentation that will eventually produce HTML documentation in the docs/build folder.  See our  :doc:`nox guide <prog_nox_docs>` about our use of nox in healthy-meals.  We use the `github pages <https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site>`_ style of docstrings for the documentation of healthy-meals.  The details of the steps that we follow to generate the documentation are:

#. Sphinx is used to generate the documentation, which ends up as HTML pages in the docs directory.  We have a nox automation command that does all of this:

   .. code-block:: python

     "nox -s sphinxDocs"

   The sphinxDocs nox session (script) does the following:

   #. Remove all prior versions of the documentation from the docs directory:

      .. code-block:: nox

        session.run("pdm", "run", "rm", "-fr", "./docs/build")
        session.run("pdm", "run", "rm", "-fr", "./docs/source")
        session.run("pdm", "run", "cp", "-R", "./docs/sphinx_src/", "./docs/source/")

      These commands first remove the source and build directories from the docs directory.  We then copy all of the files in the docs/sphinx_src directory into a new clean docs/source directory.

   #.


First, confirm you are in the root directory (directory containing manage.py)
    Note: The Sphinx setup was initially run with the command `sphinx-quickstart docs`, making `docs/` as the documentation folder.
    This means that when generating the documentation you should:

    - be in the root directory of the project (where manage.py exists).
    - specify the doc directory location ( --directory=docs, or -C docs)

    The sphinx extension `apidoc <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`_ is used to automatically document code using signatures and docstrings from the code, and place it in .rst files (and then later into .html files).

    We needed an exclusion list of modules to ignore because we are not using an apps/ folder.
    This is because we are following the standard django structure (to have all apps off of root):
    `djangoproject.com (Creating an app). <https://docs.djangoproject.com/en/2.2/intro/tutorial01/#s-creating-the-polls-app>`_ .
    All exclusions are listed after the '.' (the root folder) see `docs/Makefile` and `docs/source/conf.py`.

To Build the Documentation:

We will use nox to run the sphinxDocs automation session, which will:
- remove the build and source directories within docs
- copy in our manually created rst files into a new docs/source directory from docs/sphinx_src
- run nox -s testing to run all of the tests, coverage and generate their badges
- run nox -s genNoxDocs to list all of the automations that nox can do.
  - note we create a text file of the nox --list command to display all of the commands (sessions)
  - Note: we need to do this because sphinx autodoc does not extract the docstrings from noxfile.py.
- run sphinx-apidoc to extract docstrings from the project source files into .rst files in the docs/source directory.
- run the sphinx-build to generate html in the docs/build directory from the .rst files in the docs/source directory.
- This is all done by the following nox command:

.. code-block:: shell

    nox -s sphinxDocs

    # or using Docker
    nox -s dockerMakeDocs

    # or using make
    make apidocs --directory=docs
    make html --directory=docs

To Rebuild the Documentation (ensures all old links and pages are gone):

.. code-block:: shell

    nox -s remakeDocs

    # or using Docker
    nox -s dockerRemakeDocs

    # or using make
    make apidocs --directory=docs
    make allhtml --directory=docs

The final HTML documention main index page is generated to: `docs/build/html/index.html`

   # or alternatively
   make -C docs

   # or alternatively
   make html --directory=docs

   # or alternatively
   make html -C docs

   # or manually
    sphinx-build -M html docs/source docs/build

Notes:
- you may want to review the output of the make for warnings or errors
- If you have added any new apps, you should add them to the index.rst file, so they are available at the top level of documentation.
- They will automatically show up in docs/source/modules.rst without titles like the ones in docs/source/index.rst






The Sphinx toolset provides the capability of doing this using:

- the `Toc Tree @ documentation.help <https://documentation.help/Sphinx/toctree.html>`_ extension to manage a Table of Contents.
- the `sphinx autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_ extension to extract the documentation as well as extract documentation from the code itself.
- the `sphinx apidoc <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`_ extension to generate the documentation in the form of .rst (`restructured text <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html>`_ files).
- the `sphinx napoleon <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/>`_ extension to allow for rst, google or numpy style documentation.



Understanding the custom .rst anc config files (docs_guide.rst, index.rst, and conf.py)
---------------------------------------------------------------------------------------

The index.rst file is a customized version of the initial one created by sphinx-quickstart.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It has a table of contents that looks like:

.. code-block:: rst

    Table of Contents
    -----------------

    .. toctree::
    :maxdepth: 2
    :caption: Contents:

   Quality Assurance</qa>
   Index<genindex>
   Module Index<modindex>
   User Accounts Module</accounts>
   Misc. Pages Module</pages>
   Tests Module</tests>
   Programmers Guide<prog_guide>
   Documentation Guide</docs_guide>

The Table of Contents (TOC) is what shows up in the sidebar navigation.  It has been customized in the following ways:

- the custom ``qa`` tool (labeled ``Quality Assurance``) has been placed at the top to provide access to the testing reports.
- the ``genindex`` tool (labeled ``Index``) standard utility to provide an index to the entire project.
- the ``modindex`` tool (labeled ``Module Index``) standard utility to provide an index to all modules of the project.
- the ``/accounts`` apidoc generated file (``User Accounts``) module for the Custom User accounts.
- the ``/pages`` apidoc generated file (``Misc. Pages``) module for simple pages such as home, or about.
- the ``/tests`` apidoc generated file (``Tests``, automated testing doc strings generated documentation.
- the custom ``/docs_guide`` (this Documentation Guide file) is added to introduce the documentation philosophy of healthy-meals, and provide a step by step breakdown of the documentation process.

Note the format of the entries in the TOC is as follows:  "The Name With Spaces<[optional /]rst_filename_without_extension>"

- The name to display in the TOC.
- the name of the .rst file (without the .rst extension) is contained within "<" and ">".
- the name may have a leading optional "/" to ensure that it is always in the (main) TOC.

We build the sphinx .rst files in the docs/source, then build html into the docs/build/html directory.

CAUTION: Do not remove the following files in the docs/source directory, as these are custom files:

- conf.py - is the configuration file for Sphinx.
- docs_guide.rst - is this document.
- index.rst - is the parent .rst providing the TOC for all documentation.
- prog_guide.rst - is the start of programmer documentation, starting with the nox automation documentation.
- qa.rst is a custom .rst file to integrate in the pytest reports


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `Sphinx Raw Directive <https://sphinxfeatures.readthedocs.io/en/latest/Raw%20Directive.html>`_ is
used to have custom HTML for linked images placed initially  for the Quality Assurance page.

Linking is provided using `Link Documentation <https://sublime-and-sphinx-guide.readthedocs.io/en/latest/references.html>`_.

Code can be displayed using `Code Blocks <https://ikerdocs-sphinx.readthedocs.io/syntax/code.html>`_.


Sphinx & Restructured Text (rst) guides and resources:
------------------------------------------------------

- `sphinx tutorial <https://sphinx-tutorial.readthedocs.io/>`_.
- `Sphinx Docs <https://www.sphinx-doc.org/en/master/index.html>`_.
- `Sphinx @ documentation.help <https://documentation.help/Sphinx/index.html>`_.
- The excellent `Google Style Python Docstrings <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_.
- The `sphinxcontrib Module <https://sphinxcontrib-django.readthedocs.io/en/latest/readme.html>`_.
- `Sphinx Idiots Guide <https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/>`_.
- `ianhopkinson.org.uk <https://ianhopkinson.org.uk/2021/09/python-documentation-with-sphinx/>`_.
- `sphinx rtd theme <https://pypi.org/project/sphinx-rtd-theme/>`_ that is used in this project.
- One of many possible `Cheat Sheets <https://bashtage.github.io/sphinx-material/rst-cheatsheet/rst-cheatsheet.html>`_.
