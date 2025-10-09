Pull Requests (for code and documentation)
==========================================

- Start development on a new feature, bug fix, or documentation.

  - start from a fresly updated main branch:

    .. code-block:: shell

      git status
      git checkout main
      git pull --rebase upstream main
      git checkout -b <identifying_branch_name> # create new branch with all of main committed code in it

  - or reuse an existing related branch:

    - :code:`git status; git checkout <identifying_branch_name>; git pull --rebase upstream main`

    .. code-block:: shell

      git status # make sure all code is committed before continuing
      git checkout main
      git pull --rebase upstream main; # update branch with all code that has been merged into main recently
      git checkout -b <identifying_branch_name> # create new branch with all of main committed code in it

- To merge in updates from other developers or documentors (at any time):

  .. code-block:: shell

    git status # make sure all code is committed before continuing
    git checkout <identifying_branch_name> # switch to the branch, if not there already
    git pull --rebase upstream main; # update branch with all code that has been merged into main recently

- Make a Pull Request, review, and when reviewed and approved, have it merged into the "main" branch.

  .. code-block:: shell

    git status # make sure all code is committed before continuing
    git checkout <identifying_branch_name> # switch to the branch, if not there already
    git pull --rebase upstream main; # update branch with all code that has been merged into main recently
    git push origin # push this branch into your fork of the project

  .. code-block:: text

    https://github.com/<your_github_name>/healthy-meals
    - # Create a pull request if it hasn't been created yet:
        - # click on the compare & pull request
      - # or
        - # Pull requests / New pull request / compare: <identifying_branch_name> / Create pull request
    - # Go to your pull request:
      - # Pull requests / <your pull request>

Notes:
~~~~~~

To Do for Base Starter Branch:
------------------------------

.. ToDo:: If you are looking for an issue to work on to get going in healthy-meals, consider the following:

  - enhance documentation regularly, create an issue for solution
  - getting MyPy QA/lint tool working, create an issue for solution
  - getting Ruff QA/lint tool working, create an issue for solution
  - getting any other QA tools working, create an issue for solution
  - update developer setup instructions in README.md (pip tools, not using asdf, windows, ...), create an issue for solution
  - Helpful developer guidance into readme or docs would be great., create an issue for solution
  - See if it is possible to prevent pull requests if automated testing errors, create an issue for solution
  - See if it is possible to prevent requests if coverage below a certain percentage, create an issue for solution
  - obtain 100% coverage HTML code (pending guidance from Dave)
  - change all print statements to logger statements
  - research database I18n.  See if python has a solution like ruby's https://github.com/shioyama/mobility


.. ToDo::
    Dave's todo list:
        - prevent pull requests if nox -s goodToGo fails, as this causes failure in pull request validation.
            -  added new checkStatus nox script to confirm local git status
            - write tests (with good coverage) for checkStatus
                - do we see coverage in noxfile.py?
                - https://stackoverflow.com/questions/32381251/how-to-write-unit-tests-for-gitpython-clone-pull-functions
        - obtain coverage of noxfile.py, and mark nox (docker?) tests as slow tests
              - (done) add slow test marker code.See: tests/conftest.py & tests/nox/test_docker_nox.py
                    - https://docs.pytest.org/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option
                    - https://docs.pytest.org/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option
              - see tests/nox/test_docker_nox.py for docker nox scripts
              - see tests/nox/test_local_nox.py for local nox scripts
        - protect the BaseStarter branch
        - write guidance in programmer docs for getting coverage of HTML files
        - deploy website to lifeguides.info
        - add project and lifeguides to tayloredwebsites.com
        - github pages cleanup
              - do not overwrite production docs during pull requests
              - consider having pull request version of documentation for review
              - delete docs build artifact after upload to pages (maybe it needs a name and delete artifact action?)
        - turn on circle CI validation
        - consider turning on other CI
