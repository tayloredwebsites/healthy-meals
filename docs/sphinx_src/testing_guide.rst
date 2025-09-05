Automated Testing Guide
=======================


Automated Testing Philosophy
-----------------------------

Although there is a defacto standard to have 70% automated testing coverage of your code, I believe this is not sufficient.  I believe that if you have written the code, it should have near 100% coverage.  I will expand upon this as this project proceeds.

However, I have found that there is one obvious exception to the importance of having 100% coverage, which is when validating parameters in a function.  If we are writing a library, with a function that is designed to work anywhere, yes, it needs to have strict adherence to testing all possible values.  If however, we are writing a function for an application, it makes sense to validate the parameters coming in, but it does not make sense to write tests that have nothing to do with how the functions are being used.

At the start of this project, I we have 100% coverage of the python code (the Accounts module) in this project, but only about 70% if you include the HTML code (hopefully soon to be remedied).  I believe that there is a strong argument for HTML code coverage



Preferred Testing Tools
-----------------------

It seems that both UnitTest and Pytest are both sufficiently good tools to use.  I duplicated the tests in the Accounts module for each of the tools, and you can see that they both provide the same functionality.
- I have found Pytest easier to read, and so far have not needed test setup and breakdown feature in UnitTest.  For this reason, I will be choosing to write my test using pytest.
- If I or another developer either needs test setups and breakdowns, or strongly prefers UnitTest, they should code in UnitTest.  If using UnitTest, please try and use the pytest assert statement, instead of the UnitTest's self.assert...().  We can use the pytest assert statement, because we run all tests (pytest and UnitTest) through pytest.

- `Effective Python Testing with pytest <https://realpython.com/pytest-python-testing/>`_


Test Driven development
-----------------------

Test Driven development is an important concept to understand, and implement at best fits your coding style.

- I have often found it hard to write tests before the code, because, I often do not know what results that should be tested will look like until I have written the code.  When I am in this situation, and I find myself in the situation where I have started modifying the results to what they should be, is exactly when I turn what they should be into the test results.
- Always use test driven development on bug fixes.  Write the test so that the results are how they should be.  Run the current code on it, and it will fail.  Code the bug fix, and run the code, and the code passes.  The software now has a test to detect the bug that was just fixed, and it was simple and straight forward to do!!!

- `Test Driven Development <https://www.geeksforgeeks.org/software-engineering/test-driven-development-tdd/>`_
- `Test Driven Development (Wikipedia) <https://en.wikipedia.org/wiki/Test-driven_development>`_


Testing Process
---------------

To run the automated tests:

.. code-block:: shell

    "nox -s testing"

To run pytest in verbose mode:

.. code-block:: shell

    "uv run pytest -v"

Note: the verbose listing will list each test that is run.

To run a single test with print statements output, copy the (long) name of the test that was printed out in verbose mode <long_test_name>, and paste it into the following command:

.. code-block:: shell

    "uv run pytest -s <long_test_name>"


Viewing Automated tests, Coverage, and other reports:
-----------------------------------------------------

To generate all of the documentation, which includes the Automated test reports, Coverage reports, etc,:

.. code-block:: shell

    "uv run nox -s sphinxdocs"

To view the documentation

1. double click the docs/build/index.html file.
2. In your browser, you will see all of the documentation that will eventually be sent to `Github Pages <https://tayloredwebsites.github.io/healthy-meals/index.html>`_
3. The Quality Assurance Item will contain the testing, coverage, (and other QA reports when configured to run)
