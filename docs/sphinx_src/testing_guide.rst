Automated Testing Guide
=======================

Automated Tests as Documentation
--------------------------------



I believe that automated test are a valuable form of documentation.
    - Automated tests are written to meet the requirements of the software.  Please note that ideally the requirements are written to meet the purpose(s) of the software.  Assuming that the tests are meeting the requirements of the software, which are also meeting the requirements of the purpose(s) of the software.
    - Thus by reviewing all of the tests, we can see how the software meets the purpose(s) of the software.
        - By organizing the tests so that they cover all of the requirements (or purposes), by going through the tests, we can now see how all of the purposes
    - see: https://en.wikipedia.org/wiki/Software_quality


Automated Testing Philosophy
-----------------------------

Although there is a de facto standard to have 70% automated testing coverage of your code, I believe this is not sufficient.  I believe that if you have written the code, it should have near 100% coverage.  I will expand upon this as this project proceeds.

However, I have found that there is one obvious exception to the importance of having 100% coverage, which is when validating parameters in a function.  If we are writing a function for an application (not a library), it does not make sense to write tests that have nothing to do with how the functions are being used.  It would however make sense to have standard validations of parameters coming into the function for possible future use (or prevention of abuse).  However, if you see the strong potential that a function might eventually belong in a library, then I would say that it would be very important to write all of the unit tests for the function in a proper test driven mode so that all of the nuances and edge cases of the code are validated.

It is always best to do documentation as the code is being written, or just after fully reading and reviewing the code, and especially both when being written, and again when reread and reviewed.  This applies to testing, because testing is documentation!

At the start of this project, I we have 100% coverage of the python code (the Accounts module) in this project, but only about 70% if you include the HTML code (hopefully soon to be remedied).  I believe that there is a strong argument for HTML code coverage.  Additionally, I would like to work on extending automated testing to include other aspects of software development, including all of the tools being used, such as nox automation.  I have been making an initial go at this, by at least having nox automation scripts at least tested (if posssible).  I would like to also extend this, to detect obvious configuration errors, that will break the functionality of the tools.  I will be expanding upon this as we go.


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

Note: the verbose listing will list the full 'long_test_name' of each test that is run.

To run a single test with print statements output, copy the <long_test_name> of the test that was printed out in verbose mode <long_test_name>, and paste it into the following command:

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
3. The Quality Assurance Item will contain the testing, coverage, (and other QA/linting reports when configured to run)


Automated tests todo items:
-----------------------------------------------------

.. todo:: debug issue with logging in CustomUsers in pytest client post tests

    .. code-block:: python

        resp = client.post('/accounts/login/', {
            csrf_elem['name']: csrf_elem['value'],  # csrf token
            'email': SUPERUSER_EMAIL,
            'password': SUPERUSER_PASSWORD,
        }, follow=True)
        assert resp.status_code == 200, 'Error, login page did not return 200 OK'
        # Error. testing login post does not authenticate user, and keeps user at login page.
        assert resp.wsgi_request.user.is_authenticated, (
            'User should be authenticated')
        soup = BeautifulSoup(resp.content, 'html.parser')
        logger.debug(f'page: {soup}')
        # confirm we are on the home page
        assert soup.find('h2').get_text() == 'Home', 'Error, we are not on the home page'
        # confirm we have change password and logout links available
        assert len(elem_menu.find('a', href='/accounts/password/change/')) == 1, (
            'Should be logged in showing Password Change Button')
        assert len(elem_menu.find('a', href='/accounts/logout/')) == 1, (
            'Should be logged in showing Logout Button')
        assert elem_menu.find('a', href='/accounts/login/') is None, (
            'Should be logged and not showing Login Button')
        assert elem_menu.find('a', href='/accounts/signup/') is None, (
            'Should be logged and not showing Signup Button')
