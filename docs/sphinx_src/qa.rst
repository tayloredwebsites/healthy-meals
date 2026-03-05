Quality Assurance (QA) Guide
============================

Testing Summary Report
----------------------

.. raw:: html

    <a href="tests/index.html">
        <img src="tests/tests_badge.svg" alt="Automated Testing Report"/></a>

Python Code Coverage Report
---------------------------

Note: no coverage of noxfile.py nox configuration file.

.. raw:: html

    <a href="coverage_py/html/index.html">
        <img src="coverage_py/coverage_badge.svg" alt="Python Code Coverage Report"/></a>


Python Code & HTML Coverage Report
----------------------------------

Note: Coverage includes Template HTML files (no noxfile.py coverage also).

.. raw:: html

    <a href="coverage/html/index.html">
        <img src="coverage/coverage_badge.svg" alt="Python Code & HTML Coverage Report"/></a>


Software Quality, Reliability, and End User Requirements
--------------------------------------------------------


Definition of Quality Assurance
=> The assurances do we have that the software is of good quality
=> That the software (reliably????) gets a good grade in meeting software expectations of what makes the software good.
=> The accumulation of the grade measurements of the expectations that makes the software good.
=> The accumulation of the grade measurements of the criterion that best specify the software expectations.
=> The accumulation of the grade measurements of the criterion that best specify the software expectations of all users of the software (End Users).
=> The accumulation of the grade measurements of the End User Requirements.

=> End User Requirements == the criterion that best specify the software of all users of the system.

Software Quality Reliability
=> The variance of the accumulation of the grade measurements of the End User Requirements in all of the known possible circumstances, repeatedly.


Software Purpose
----------------

There is no reason that we could expect that all user expectations would never conflict with one another.  To resolve this, we need a Software Purpose.

Usability is a measure of expectations
  - changes over time, so there needs to be change management
  - different users have different expectations, including software owners.
  - expectation must be explicitly stated, otherwise they cannot be detected and measured
  -

Set of Criterion == Software Requirements


The question then becomes, how can a bunch of End User Requirements represent one or more large purposes?  I expect that by breaking up a large purpose into Goals, and Tasks, in which End User Requirements are placed, we have a structure that seems uncontroversial.  To ensure that all code meets the purpose(s) of the application,we will want to ensure all code belongs somewhere within this structure.  Note, because any code, requirement, task, or goal may not necessarily belong to just one requirement, task, goal, or purpose, we do not have a tree structure, but a Directed Acyclic Graph.

The next question then is what about all of the other requirements that would be required for the software to function and be available to the user, to be secure, to be reliable, to be easy to use, to work as expected, etc?



  - user processes and goals as Main Purposes and Requirements
    - goals are cohesive
    - processes guide user to meet goals
    - able to do all of the processes successfully
  - usability as requirements
  - server issues as requirements
  - security issues as requirements
  - software maintainability as requirements
  - Testing as Documentation
  - User documentation as model for tests
  - Code as Documentation for programmer, IT, and User docs.


Quality of code, tests, and documentation
  - code as user docs
    - quality of documentation impacts the usability of the website if user docs or maintainability if code docs.
      - Note, that if the website is most usable when how to start a process for a goal is obvious on the page (without user docs).
      - thus user docs as code
  - code as programmer docs

  - testing as both user docs, and developer docs

  - is there a necessary duplication of testing as docs with the concept of code as docs?
    - testing docs are not visible to the user or developer when coding
    - user processes are in user docs, and preferably coverage of all user processes in matching testing flows.
    - should code be written so that it has matches to user processes?
