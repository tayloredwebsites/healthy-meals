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

  - ongoing enhancements to documentation
    - Helpful developer guidance
    - better coverage
    - improved developer setup instructions
      - pip tools being used with UV?
      - replace asdf with UV 
  - getting MyPy QA/lint tool working
  - getting Ruff QA/lint tool working
  - getting any other worthwhile QA tools working
  - update developer setup instructions in README.md (pip tools?, not using asdf, windows, using hatch, ...)


.. ToDo:: Dave's todo list:

  - write guidance in programmer docs for getting coverage of HTML files
  - github pages cleanup
      - do not overwrite production docs during pull requests
      - consider having pull request version of documentation for review
      - delete docs build artifact after upload to pages (maybe it needs a name and delete artifact action?)
  - turn on circle CI validation
  - consider turning on other CI
  - nox automated testing coverage
    - confirm all scripts have a returncode of 0
    - note slow docker scripts!
  - nox "status" script to validate git environment
    - remotes set up properly
    - current local branch up to date for pull requests
    - main branch up to date for pull requests
    - warning to not do pull request if automated testing errors
    - warning to not do pull request if coverage below a certain percentage
    - handle updates to new "starter" branch
