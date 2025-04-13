Pull Requests (for code and documentation)
==========================================

Long Running Branches (not feature or code update temporary branches):
----------------------------------------------------------------------

Long Running Branches Purposes:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

  "main" branch - Long running source of truth for both code and docs are maintained in this branch.
    \
    "code" branch - Long running source of truth for code. See: Note 1
      \
      "<codeFeature>" branches - short term branches for updates to code are done here. See: Note 1
    \
    "docs" branch - Long running source of truth for documentation.
      \
      "<docsUpdate>" branches - short term branches to create or update documentation.


project code and documentation update flow overview:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Main Commit and Pull Request Flow:

- "code" long running branch -\> <codeFeature> temporary branch.

  - Updates to code are started by creating (or reusing) a "<codeFeature>" branch off of the main "code" branch for that code feature.

    - create a new feature branch:

      - :code:`git checkout code; git pull --rebase upstream code; git checkout -b <codeFeature>`

    - or reuse the same feature branch:

      - :code:`git checkout <codeFeature>; git pull --rebase upstream code`

  - Developers will repeatedly do pushes to github for the <codeFeature> branch until the feature is ready.
  - :code:`git push origin <codeFeature>`

- "<codeFeature>"" temporary branch -\> "docs" long running branch

  - When programming is completed, a pull request is created, approved, and merged from "<codeFeature>" to the "docs" permanent branch.

- "docs" long running branch -\> "main" long running branch

  - "Documentation Update Loop":

    - Obtain documentation for <codeFeature> branches by pulling in the latest docs branch to the local repo.

      - new branch:

        - :code:`git status; git checkout docs; git pull --rebase upstream docs; git checkout -b <docsUpdate>`

      - or reuse branch:

        - :code:`git status; git checkout <docsUpdate>; git pull --rebase upstream docs`

    - To merge in updates from other developers or documentors:

      - :code:`git status; git pull --rebase upstream docs}`

    - Review and update documentation (in project code and in docs folder).
    - Update github pages with the updated documentation:

      - :code:`git push origin <docsUpdate>`

    - Make a Pull Request, review, and when ready, merge it into the "docs" branch.

      - Note: Automatically, the github pages site is updated shortly after pushes to the docs branch.
      - Github pages documentation is reviewed.
      - if github pages documentation is good, go to the next stop to make the pull request to "main".
      - else loop back to the "Documentation Update Loop" reuse the <codeFeature> branch for more updates.

  - When documentation is good, a Pull request will be created, approved, and merge the "docs" permanent branch into the "main" permanent branch.

- "main" long running branch -\> "code" long running branch.

  - As soon as the "docs" permanent branch into the "main" permanent branch:

    - the "main" permanent branch will be merged into the "docs" permanent branch.
    - The code update cycle will be complete.


Notes:
~~~~~~

- Documentation in "docs" folder is not updated to github in the "code" branch (or its child branches).

  - "code" branch of docs/.gitignore is set to not push the docs folder to github.

    - docs/.gitignore ignores all files, except the .gitignore (in the docs directory).

  - "docs" branch of docs/.gitignore is set to push all files from the docs folder to github.

    - docs/.gitignore file does not ignore any files in the docs directory.

- Do NOT merge "<codeFeature>" branch back into the "code" (or the "main") branch.

  - This is because the "code" branch needs to have the documentation updates, which are done later in the "docs" branch.
  - The "main" branch will be updated from the "docs" branch, and the "code" branch will be updated from the "main" branch.

- Pull Request - Prevention of git problems:

  - all pushes in normal flow do not touch .gitignore in docs branch.

- Problems with docs/.gitignore:

  - If docs/.gitignore ever updated
  - Or if any long running branch has the wrong docs/.gitignore
  - Then:

    - stop all use of "code" branch.
    - Make sure the "main" branch has the correct docs/.gitignore.  if not:

      - create a fix branch off of the "main" branch.
      - update the docs/.gitignore file (copy .gitignore.main_branch to .gitignore).
      - create and update a pull request to update the main branch.
      - merge the pull request to put the updates into the "main" branch.

    - Create and merge a pull request from "main" to "code".
    - Make sure the "code" branch has the correct docs/.gitignore.  if not:

      - create a fix branch off of the "code" branch.
      - update the docs/.gitignore file.

        - copy .gitignore.docs_branch to .gitignore in the "code" folder.
        - Note: the docs/.gitignore will be listed in git status, because it is the one file that goes to github in the code branches.

      - create and update a pull request to update the "code" branch.
      - merge updates into the "code" branch.
      - Make sure that all "<codeFeatures>" branches are up to date with the updated "code" branch bydoing the following rebase:
        - :code:`git pull --rebase upstream code`
        - confirm that the docs/.gitignore is correct.
        - confirm that the feature code works as before.

    - Create and merge a pull request from "main" to "docs"
    - The "docs" branch should now have the correct docs/.gitignore.


Pull  Request preparations.
---------------------------

Nox prPrepare command
~~~~~~~~~~~~~~~~~~~~~



See `Guide to pre-commit hooks <https://www.slingacademy.com/article/git-pre-commit-hook-a-practical-guide-with-examples/#google_vignette>`_.

.. code-block:: shell
  # set up git pre-commit hook

To Do for next pull request:
----------------------------

.. todo:: Enhance Sphinx generated documentation as we go.

.. todo:: docs branch pull requests Step 1:

  - all of docs are going to docs
  - turn on circle ci validation
  - turn on other ci from github
  - confirm docs/.gitignore is correct for docs branch

.. todo:: docs branch pull requests Step 2:

  - nox commands work in docker
  - Prevent pushes to docs and main
  - prevent commits to docs and main
  - automatic pull rebases from upstream
  - automatic pr pushes to origin
  - confirm docs branch deploys to pages
  - confirm top  nav to docs works
  - consider putting index page at root of docs?
  - confirm website link to docs works with styles working
  - consider fixing all nox items, especially docker (with PDM changes)
  - turn on and get circle  CI going again
  - turn on github actions and get github CI going again
  - consider pre-commits to prevent problems with docs/.gitignore - https://pre-commit.com/

.. todo:: research:

  - consider validation of docker environment before pull request merges
