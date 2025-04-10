
Nox automation
==============

We chose to use `Nox <https://nox.thea.codes/en/stable/tutorial.html>`_ seems to be the defacto automation tool, especially for python testing.

`nox <https://nox.thea.codes/en/stable/tutorial.html>`_ is the automation tool we use generate or update the documentation that will eventually produce HTML documentation in the docs/build folder.  See our  :doc:`nox guide <prog_nox_docs>` about our use of nox in healthy-meals.  We use the `github pages <https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site>`_ style of docstrings for the documentation of healthy-meals.

Instructions: to run a nox automation function listed below, the format of the command is:

.. code-block:: shell

   nox -s <noxCommand>

Note: any functions descriptions that have a trailing :code:`>:(`, indicates the functions need repair since the PDM install


.. literalinclude:: ../qa/nox_docs.txt
   :lines: 5-