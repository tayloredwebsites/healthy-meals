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

  - enhance documentation regularly, create an issue for solution outside of existing standards
  - getting MyPy QA/lint tool working, create an issue for solution outside of existing standards
  - getting Ruff QA/lint tool working, create an issue for solution outside of existing standards
  - getting any other QA tools working, create an issue for solution outside of existing standards
  - update developer setup instructions in README.md (pip tools, not using asdf, windows, ...), create an issue for solution outside of existing standards
  - Helpful developer guidance into readme or docs would be great., create an issue for solution outside of existing standards
  - See if it is possible to prevent pull requests if automated testing errors, create an issue for solution outside of existing standards
  - See if it is possible to prevent requests if coverage below a certain percentage, create an issue for solution outside of existing standards
  - obtain 100% coverage HTML code (pending documentation and examples from Dave)
  - Write up an issue for something that would improve Healthy Meals
  - Contact `Dave @ Taylored Web Sites <mailto:tayloredwebsites@me.com>`_ if you wish to share some thoughts, or help on the project.


.. ToDo:: Dave's todo list:

  - pull request to update github pages documentation
  - analysis of pull request 46 run of .github/workflows/djangoUvCi.yml failure, to help prevent it in the future
    - run nox -s goodToGo successfully
    - run uv sync? locally (or ?), to ensure that installed modules locally match modules in github workflow.
  - obtain good coverage of noxfile.py
  - nox -s status for improved git status message for git warnings against potential git repo problems.
  - write guidance in programmer docs for getting coverage of HTML files
  - review need for utils/docker_clear.py
  - create starter branch before working on core programming.
  - start on first core table: references (References).
