Quality Assurance (QA) Guide
============================

Note: we generate two separate coverage reports.  We do this because:
  - Most projects  check for the coverage of only python files, which can be found in the docs/build/coverage folder.
  - I have found that there is substantial sources of bug in other files ( .html template files, and .txt template files).
    - A better coverage report that includes these files can be found in the docs/build/coverage_py folder.

Testing Summary Report
----------------------

Note: Click on image to see report.

.. raw:: html

    <a href="tests/index.html">
        <img src="tests/tests_badge.svg" alt="Automated Testing Report"/></a>

Python Code Coverage Report
---------------------------

Note: Click on image to see report.

.. raw:: html

    <a href="coverage_py/html/index.html">
        <img src="coverage_py/coverage_badge.svg" alt="Python Code Coverage Report"/></a>


Better Coverage Report (python files plus also .html & .txt files)
----------------------------------

This Coverage Report includes Python files, Template HTML files, and also .txt template files.

Note: Click on image to see report.

.. raw:: html

    <a href="coverage/html/index.html">
        <img src="coverage/coverage_badge.svg" alt="Python Code & HTML Coverage Report"/></a>
