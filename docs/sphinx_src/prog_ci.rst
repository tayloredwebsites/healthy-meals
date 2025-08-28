Continuous Integration (CI)
===========================

Testing, Coverage, and Documentation generation
-----------------------------------------------

The `nox -s genNoxDocs` command currently generates of the documentation and quality assurance reports (see the :doc:`Quality Assurance Guide</qa>`) for local viewing (see :doc:`Documentation Guide</docs_guide>` ).  To deploy these, the docs branch is configured to automatically deploy the docs branch to our `Github Pages <https://tayloredwebsites.github.io/healthy-meals/build/index.html>`_.  We have circle CI automatically run the pytest tests to ensure that pull requests are only merged when there are no errors.
