
Nox automation
==============

We chose to use `Nox <https://nox.thea.codes/en/stable/tutorial.html>`_ seems to be the defacto automation tool, especially for python testing.

`nox <https://nox.thea.codes/en/stable/tutorial.html>`_ is the automation tool we use generate or update the documentation that will eventually produce HTML documentation in the docs/build folder.  See our  :doc:`nox guide <prog_nox_docs>` about our use of nox in healthy-meals.  We use the `github pages <https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site>`_ style of docstrings for the documentation of healthy-meals.  The details of the steps that we follow to generate the documentation are:


.. literalinclude:: ../qa/nox_docs.txt
   :lines: 5-