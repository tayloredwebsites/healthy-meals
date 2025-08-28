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
----------------------------

.. ToDo:: Enhance Sphinx generated documentation as we go.

.. ToDo:: Base Starter:

  - turn on circle ci validation
  - turn on other ci from github
  - confirm nox commands work in docker
  - Prevent pull requests if errors
  - prevent pull requests if coverage below a certain percentage
