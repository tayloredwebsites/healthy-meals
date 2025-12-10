Documentation Guide
===================


Code Documentation Philosophy
-----------------------------

The philosophy of documentation in the Healthy Meals project includes the following thoughts:

The code should be written to be part of the documentation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - see: `Docs as Code <https://www.writethedocs.org/guide/docs-as-code/>`_
  - see: `Fowler, Code as Docs <https://martinfowler.com/bliki/CodeAsDocumentation.html>`_

Code should be written to be read.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Readability: As I am writing code, and end up reading some related code, I sometimes realize that what what the code is saying is not very clear.

  - If the issue is simply that a docstring or comment statement needs to be clarified, it should be updated immediately, and appropriate notes included in the commit and pull request.  This helps ensure code clarity without risking delayed or lost documentation updates.

  - Refactoring: I have found the following rules to be helpful in deciding when and how to refactor code:

    - Never refactor code until there are a few sets of duplicated code.
    - Only change a functions interface (name, parameter names, or parameter functionality) when:

      - If backward compatibility is an issue, this should be reviewed by the team or senior developer.  If agreed this is a good time to do the interface change, a new function should be created, and the old function should be deprecated.
      - If the name of the function has a confusing or misleading name, it should (hopefully, eventually) to be changed to have a more descriptive name.
      - If the parameters of the function do not describe what they are or how they fit into what the function is doing, they should also (hopefully, eventually) be changed.

    - Never put functionality into a function unless it is being used right now.  This will ensure that:

      - all of the appropriate automated testing can be correctly written.
      - only required, and well understood code features are put into the code.

    - Normally put refactoring code at least in a separate commit, and consider putting it in a separate pull request (by creating a `.. todo::` item or an issue for a large amount of code).

PEP 8
~~~~~

In general, I treat `PEP 8 <https://peps.python.org/pep-0008/>`_ as a warning if it is not part of project standards.

- Note: In the PEP 8 link above, it says:

  A Foolish Consistency is the Hobgoblin of Little Minds

  One of Guido’s key insights is that code is read much more often than it is written. The guidelines provided here are intended to improve the readability of code and make it consistent across the wide spectrum of Python code. As PEP 20 says, “Readability counts”.

  A style guide is about consistency. Consistency with this style guide is important. Consistency within a project is more important. Consistency within one module or function is the most important.

  However, know when to be inconsistent – sometimes style guide recommendations just aren’t applicable. When in doubt, use your best judgment. Look at other examples and decide what looks best. And don’t hesitate to ask!

  In particular: do not break backwards compatibility just to comply with this PEP!

  Some other good reasons to ignore a particular guideline:

    1. When applying the guideline would make the code less readable, even for someone who is used to reading code that follows this PEP.
    2. To be consistent with surrounding code that also breaks it (maybe for historic reasons) – although this is also an opportunity to clean up someone else’s mess (in true XP style).
    3. Because the code in question predates the introduction of the guideline and there is no other reason to be modifying that code.
    4. When the code needs to remain compatible with older versions of Python that don’t support the feature recommended by the style guide.

- `line-too-long (E501) <https://docs.astral.sh/ruff/rules/line-too-long/>`_  This is a controversial rule.

  - note that if you look at the description of the E501 statement, that does not meet its own requirements, because it is an explanation, not a code statement.
  - Explanations should never be limited in length so we can ensure the best possible explanation.
  - I believe that we should let the developer set the code window width as they please, and let it wrap explanations as it will, as it will be fairly readable, especially if it was written as a good explanation.
  - We should never have the developer waste any time thinking about how explanations should wrap.
  - I see the E501 rule as one that is too broad, without a good explanation and without full insight in regards to all the the aspects and issues involved.  Thus:

    - I have no problem with long comment lines, long strings, URLs, and any other non-code lines.  Examples:

      - Comments should wrap as they will, and let the user choose the width of viewable text for readability.
      - assert statements:

        - For readability, it is important to have an informative error string that is as long as necessary to describe what is being tested.  Do not even think about shortening your explanation, think about how readable it is!!!!
        - When I see an assert statement, personally do not care if the explanation of the error being checked is wrapped.
        - It is nice to be able to the assert code on the first line, and the explanation indented on the next line (which is as long as necessary).  This makes reading the assert statements easy to read.

      - etc.  (feel free to add to this).

- The `commented-out-code (ERA001) <https://docs.astral.sh/ruff/rules/commented-out-code/>`_.

  - I sometimes leave in commented out logger.debug statements.

    - Why I use logger.debug statements:

      - I use logger.info and logger.debug statements in the code to assist in following the flow of (longer) tests.  This is helpful because I often use longer tests to minimize test setup and shut down time.
      - if I have tests or code with debug statements that were involved in resolving a bug, I will often leave the debugging code in if I think it will help debugging issues in the future
      - However, I will comment out logger.debug or logger.info statements when the output they produce clutter the test flow logging (especially when it produces a lot of output).

  - I sometimes leave in time.sleep statements in Selenium tests, to give enough time see the output page in the middle of a selenium test (for future debugging purposes).

  - Any existing print() statements should be removed or converted to logger.debug, logger.info, or logger.error as appropriate.
  - Sometimes issues are found when reading code, such as a project standard, a small refactor, a clean up of messy or unclear code.  If such issues are found, and the issues do not exist in an existing project issue or `.. todo::` item, then:

    - if any developer sees a small issue with the code, the developer may place (near the code) a docstring with:

      - a `.. todo::` item to describe the issue to resolve
      - possibly include any suggestions for how best to resolve it.
      - if the developer is a senior developer, they may additionally add code (suggested, or attempted) into a `..  code::` section, with any current or potential issues with that code.
      - put an appropriate note in their current pull request, or preferably create a new pull request (if it is not too disruptive to the current issue being worked on).

    - if any developer sees a large issue with the code, they should create an issue, being sure to add notes about any possible related issues.  This issue should:

      - describe the issue clearly
      - note how the issue may relate to other issues, if appropriate.
      - include references to the program file names, Class Names, and other identifying aspects of the issue.

    - if a senior developer sees there is a code change is to meet existing standards, and the amount of changes appear small enough, a senior developer may fix the code.  This will require updating all appropriate documentation, putting a note in the pull request, and have automated testing for coverage and edge cases.
    - If a senior developer sees any commented out code for a potential future large enhancement, it should be separated out into a repository branch, in its own pull request, with an appropriate issue created as necessary, and with a pull request started.


Code Documentation Process Overview
-----------------------------------

Google Docs Style Docstrings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The choice to use the google style documentation was motivated by an sphinx article on `napoleon legible docstrings <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/#google-vs-numpy>`_.  It is recommended to use one style through out a project I have chosen the `google style <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_ which seems to be more popular, especially for non-scientific applications.

Using docstrings for code documentation:

  - Use `Google Style Python Docstrings <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_.
  - See `Describing code in Sphinx <https://www.sphinx-doc.org/en/master/tutorial/describing-code.html>`_.
  - The Sphinx toolset recognizes `NumPy <https://numpy.org/doc/stable/>`_ , `Google <https://google.github.io/styleguide/pyguide.html>`_ , and `rst <https://peps.python.org/pep-0287/>`_ code documentation standards.
  - The `Napoleon <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/>`_ extension to Sphinx extension us used allows us to use the `Google Python Style Guide <http://google.github.io/styleguide/pyguide.html>`_.
  - When code has docstrings appropriately placed within it, Sphinx will automatically pull them into the documentation in the docs directory.
  - The healthy-meals github repository has been set up to automatically deliver the documentation to a `github pages site on the internet <https://tayloredwebsites.github.io/healthy-meals/build/index.html>`_.


Example Google Style Docstrings:
----------------------------------------------

This demonstrates documentation as specified by the `Google Style Python Style Guide <http://google.github.io/styleguide/pyguide.html>`_.


Docstrings In General:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    '''Summary of docstring.

    Docstrings may extend over multiple lines.
    Sections are created with a section header and a colon followed by a block of indented text.

    Literal Text Block::

        Literal Text blocks are created by indenting following a line ending with DOUBLE colons, and a blank line.
        They may be continued with lines at the same indentation, even after blank lines.

    .. code-block:: python

        # this is a code block to contain python code.
        res = aFunction(something, goes, in)
        print(res.avalue)

    Todo:
        * For module TODOs
        * You have to also use ``sphinx.ext.todo`` extension
    '''



Example Class Docstring:
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class ExampleClass(object):
        '''Summary of Class functionality.

        Detail description of the class functionality.

        Attributes:
            module_level_variable1 (int): Module level variables are preferably documented in
                the ``Attributes`` section of the class docstring.
        ''''
        @property
        def readonly_property(self):
            """str: Properties should be documented in their getter method."""
            return 'readonly_property'

        @property
        def readwrite_property(self):
            """:obj:`list` of :obj:`str`: Properties with both a getter and setter
            should only be documented in their getter method.

            If the setter method contains notable behavior, it should be
            mentioned here.
            """
            return ['readwrite_property']

        @readwrite_property.setter
        def readwrite_property(self, value):
            value


Example Method Docstring:
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def example_function(param1: int, param2: str):
        """Summary of the function.

        Detailed description of the function.

        Args:
            param1 (int): Description of the first parameter.
            param2 (str): Description of the second parameter.

        Note::

            - We assume that parameters will be typed for readability and code quality.
            - We do not put self in the Args section for Class level functions

        Returns:
            bool: True if successful, False otherwise.

            The ``Returns`` section may span multiple lines and paragraphs.

            The ``Returns`` section supports any reStructuredText formatting,
            including literal blocks::

                {
                    'param1': param1,
                    'param2': param2
                }

        Raises:
            AttributeError: The ``Raises`` section is a list of all exceptions
                that are relevant to the interface.
            ValueError: If param1 is not 42.

        Examples:

              $ example_function(1, "test")

              True
        """
        if param1 != 42:
            raise ValueError('param1 must be 42')
        return True


Generation of the Documentation.
----------------------------------

`nox <https://nox.thea.codes/en/stable/tutorial.html>`_ is the automation tool we use generate or update the documentation that will eventually produce HTML documentation in the docs/build folder.  See our  :doc:`nox guide <prog_nox_docs>` about our use of nox in healthy-meals.  We use the `github pages <https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site>`_ style of docstrings for the documentation of healthy-meals.  The details of the steps that we follow to generate the documentation are:

#. Sphinx is used to generate the documentation, which ends up as HTML pages in the docs directory.  We have a nox automation command that does all of this:

   .. code-block:: python

     "nox -s sphinxDocs"

   The sphinxDocs nox session (script) does the following:

   #. Remove all prior versions of the documentation from the docs directory:

      .. code-block:: text

        session.run("pdm", "run", "rm", "-fr", "./docs/build")
        session.run("pdm", "run", "rm", "-fr", "./docs/source")
        session.run("pdm", "run", "cp", "-R", "./docs/sphinx_src/", "./docs/source/")

      These commands first remove the source and build directories from the docs directory.  We then copy all of the files in the docs/sphinx_src directory into a new clean docs/source directory.

   #.


First, confirm you are in the root directory (directory containing manage.py)
    ``Caution``: The Sphinx setup was initially run with the command `sphinx-quickstart docs`, making `docs/` as the documentation folder.
    If you are not using the `nox` automations generating the documentation you should:

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

  - Note: we create a text file of the nox --list command to display all of the commands (sessions)
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

.. code-block:: shell

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
- the `sphinx todo <https://www.sphinx-doc.org/en/master/usage/extensions/todo.html>`_ extension allows for the accumulation of all doc strings (or entries in .rst files) marked as :code:`.. :Todo` to be automatically included into a `To Do List`.


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
        Modules</modules>
        Programmers Guide<prog_guide>
        Testing Guide<testing_guide>
        Documentation Guide</docs_guide>



The Table of Contents (TOC) is what shows up in the sidebar navigation.  It has been customized in the following ways:

- the custom ``qa`` tool (labeled ``Quality Assurance``) has been placed at the top to provide access to the testing reports.
- the ``genindex`` tool (labeled ``Index``) standard utility to provide an index to the entire project.
- the ``modindex`` tool (labeled ``Module Index``) standard utility to provide an index to all modules of the project.
- the ``/modules`` apidoc generated file (``healthy-meals``) modules / apps for the Healthy Meals project.
    - The modules detailed here are: {accounts - CustomUser; common; noxfile; pages; and tests}
- the custom ``/prog_guide`` (`Programmers Guide`) includes many technical details about how this project has been programmed, philosophy, standards, and the To Do list pulled from the code base and documentation.
- the custom ``/testing_guide`` is added to introduce the testing philosophy of healthy-meals, and provide a step by step breakdown of the documentation process.
- the custom ``/docs_guide`` (this Documentation Guide file) is added to introduce the documentation philosophy of healthy-meals, and describe the tools, and processes used.

Note: the format of the entries in the TOC is as follows:  "The Name With Spaces<[optional /]rst_filename_without_extension>"

- The name to display in the TOC.
- the name of the .rst file (without the .rst extension) is contained within "<" and ">".
- the name may have a leading optional "/" to ensure that it is always in the (main) TOC.

We build the sphinx .rst files in the docs/source, then build html into the docs/build/html directory.

``Note``: Sphinx requires that all of the .rst files used to build the documentation reside in the `source` directory.  Because we are using both our custom .rst files (including the `index.rst` file) and the files generated from the code using the `autodoc` toolset, this directory is a mix of files that are regenerated, as well as files that are permanent custom files.  To prevent accidental loss of any of the permanent custom files (including `index.rst`), these files are now kept in the `docs/sphinx_src` directory, and copied into the source directory when using the `nox` documentation automations.

``Caution``: Be sure to edit your .rst files in the sphinx_src directory, not the source directory.


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


Deployment to Github Pages:
---------------------------

See: `Pull Requests (in Developer Documentation) <prog_prs>`_.

For guidance on how to do Continuous Integration (Testing and validation done in the remote repo - Github), I found this page helpful: `Deploying Github Pages with Github workflows <https://dev.to/davorg/deploying-github-pages-site-with-github-workflows-3bhh>`_.  I ended up doing the following:

- I `Turned off the Jekyl workflow <https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site>`_, so that I could run the regular github workflows in the ``.github/workflows`` directory.
- I then could see my pre-existing ``.github/workflows/djangoCi.yml`` action could now run.
- I then added another github action to deploy the pages following the instructions by `davorg <https://dev.to/davorg/deploying-github-pages-site-with-github-workflows-3bhh>`_, and now (hopefully ???) the CI tests are run to ensure no automated testing errors, as well as automatic deployment to github pages.
-
