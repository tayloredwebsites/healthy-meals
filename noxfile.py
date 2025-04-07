from pathlib import Path

import os
import nox




class NoxfileDocs:

    '''NoxfileDocs class added to attempt to add docstrings to Sphinx automodule.

    noxfile Documentation:
    ======================

    Note: Currently only this class docstring shows in Sphinx

    ..todo:: Get Noxfile session docstrings to display in Sphinx

    Examples:
    ---------

    Local Server Tasks:
    ~~~~~~~~~~~~~~~~~~~

    .. code-block:: python

        # Bring up Healthy Meals locally (in local server).
        nox -s localup

        # Build documentation to Sphinx locally.
        # Note: ignore modules.rst warnings (they are manually in index.rst).
        nox -s makeDocs

        # Rebuild all documentation to Sphinx (cleans up old docs) locally.
        # Note: ignore modules.rst warnings (they are manually in index.rst).
        nox -s remakeDocs

        # Run automated tests (with test coverage) locally.
        nox -s testing

    Docker Tasks:
    ~~~~~~~~~~~~~

    .. code-block:: python

        # Bring up Healthy Meals in docker in background.
        nox -s dockerUpBg

        # Bring up Healthy Meals in docker, with log to console.
        nox -s dockerUpLog

        # Only bring up Healthy Meals in docker if not up already.
        nox -s dockerEnsureUp

        # Bring down Healthy Meals in docker.
        nox -s dockerDown

        # 'Clear out entire docker system.
        nox -s dockerClear

        # Generate the documentation using Sphinx through docker.
        nox -s dockerMakeDocs

        # Regenerate the documentation using Sphinx through docker (cleans up old docs).
        nox -s dockerRemakeDocs

        # Output docker logs out to console. (hit <ctrl>c to stop).
        nox -s dockerLogs

        # Run automated tests (with test coverage) in docker.
        nox -s dockerTesting

    '''

    ##################################################################################
    # Local Server tasks


    @nox.session(python=("3.12"), venv_backend="none")
    def setupEnv(session):
        '''Set up external environment as needed (no venv)).'''
        # os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})
        os.environ.update({"NOX_DEFAULT_VENV_BACKEND": "none"})
        session.run_always('pdm', 'install', '-G', 'test')
        session.run("pdm", "run", "manage.py", "makemigrations")
        session.run("pdm", "run", "manage.py", "migrate")
        session.run("pdm", "run","sass", "static/scss:static/css")
        session.run("pdm", "run", "manage.py", "collectstatic", "--noinput")



    @nox.session(python=("3.12"), venv_backend="none")
    def goodToGo(session):
        #: testing goodToGo docs
        ''' Check to confirm that all is good to go (for push / commit / etc.).'''
        session.run("pdm", "run", "nox", "-s", "setupEnv") # make sure pdm session is set up if needed
        session.run("pdm", "run", "nox", "-s", "remakeDocs") # generate docs locally
        session.run("pdm", "run", "nox", "-s", "testing") # run all current qa checks


    @nox.session(python=("3.12"), venv_backend="none")
    def localUp(session):
        ''' Bring up Healthy Meals in local server.'''
        session.run("pdm", "run", "manage.py", "runserver", "0.0.0.0:8000")


    @nox.session(python=("3.12"), venv_backend="none")
    def genNoxDocs(session):
        ''' Generate nox documentation into a file for inclusion into Sphinx.'''
        with Path.open("./docs/qa/nox_docs.txt", "w") as out:
            session.run("pdm", "run", "nox", "--list",
                stdout=out, # output to nox_docs.txt
            )


    @nox.session(python=("3.12"), venv_backend="none")
    def sphinxDocs(session):
        """Rebuild all documentation to Sphinx (cleans up old docs).

        Ignore the warning about modules.rst not included in the toctree,
        as modules are manually entered into index.rst

        """
        session.run("pdm", "run", "rm", "-fr", "./docs/build")
        session.run("pdm", "run", "rm", "-fr", "./docs/source")
        session.run("pdm", "run", "cp", "-R", "./docs/sphinx_src/", "./docs/source/")
        session.run("pdm", "run", "nox", "-s", "testing")
        session.run("pdm", "run", "nox", "-s", "genNoxDocs")
        session.run("pdm", "run", "make", "apidocs", "--directory=docs")
        session.run("pdm", "run", "make", "allhtml", "--directory=docs")
        # session.run("pdm", "run", "mv", "./docs/build/*", "./docs/")


    @nox.session(python=("3.12"), venv_backend="none")
    def testing(session):
        """Run automated tests (with test coverage) through docker."""
        with Path.open("./docs/qa/coverage_run.txt", "w") as out:

            # empty out tests and coverage directories
            session.run("pdm", "run", "rm", "-fr", "./docs/qa")

            session.run("pdm", "run", "coverage", "run", "-m", "pytest", "tests",
                "--junitxml=./docs/qa/tests/junit.xml",
                "--html=./docs/qa/tests/index.html",
                stdout=out, # output to ran_coverage.txt
            ) # run tests with coverage
            session.run("pdm", "run", "genbadge", "tests",
                "--input-file", "./docs/qa/tests/junit.xml",
                "--output-file", "./docs/qa/tests/tests_badge.svg",
                stdout=out, # output to ran_coverage.txt
            ) # create tests badge
            session.run("pdm", "run", "coverage", "xml",
                "-o", "./docs/qa/coverage/coverage.xml", # xml output file
                stdout=out, # output to ran_coverage.txt
            ) # create coverage.xml file
            session.run("pdm", "run", "coverage", "html",
                "-d", "./docs/qa/coverage/html/", # html output directory
                stdout=out, # output to ran_coverage.txt
            ) # create coverage HTML files
            session.run("pdm", "run", "rm", "-f",
                "./docs/qa/coverage/html/.gitignore", # ensure all files go to repo
            )
            session.run("pdm", "run", "genbadge", "coverage",
                "--input-file", "./docs/qa/coverage/coverage.xml",
                "--output-file", "./docs/qa/coverage/coverage_badge.svg",
                stdout=out, # output to ran_coverage.txt
            ) # create coverage badge


    ##################################################################################
    # Docker tasks

    @nox.session(python=("3.12"), venv_backend="none")
    def dockerUpBg(session):
        '''Bring up Healthy Meals in docker in background.'''
        session.run("docker", "compose", "up", "--build", "--detach")

    @nox.session(python=("3.12"), venv_backend="none")
    def dockerUpLog(session):
        '''Bring up Healthy Meals in docker, with log to console.'''
        session.run("docker", "compose", "up", "--build")

    @nox.session(python=("3.12"), venv_backend="none")
    def dockerEnsureUp(session):
        '''Only bring up Healthy Meals in docker if not up already.'''
        session.run("docker", "compose", "up", "--build", "--detach", "--no-recreate")

    @nox.session(python=("3.12"), venv_backend="none")
    def dockerExecSh(session):
        '''Open shell in web container.'''
        session.run("docker", "exec", "-it", "hm_web_image", "sh")

    @nox.session(python=("3.12"), venv_backend="none")
    def dockerExecPsql(session):
        '''Open psql in db container.'''
        session.run("docker", "exec", "-it", "healthy_meals_5-pg_db-1", "psql", "--dbname=healthy_meals", "--username=healthy_meals")

    @nox.session(python=("3.12"), venv_backend="none")
    def dockerDown(session):
        '''Bring down Healthy Meals in docker.'''
        session.run("docker", "stop", "hm_web_image")
        session.run("docker", "stop", "healthy_meals_5-pg_db-1")

    @nox.session(python=("3.12"), venv_backend="none")
    def dockerClear(session):
        '''Clear out entire docker system.'''
        session.run("docker", "ps", "-aq", "|", "xargs", "docker", "stop", "|", "xargs", "docker", "rm")
        session.run("docker", "system", "prune", "--all", "--force")


    @nox.session(python=("3.12"), venv_backend="none")
    def dockerMakeDocs(session):
        """Generate the documentation using Sphinx through docker."""
        session.run("docker", "exec", "-it", "hm_web_image", "toc", "-s", "makeDocs")


    @nox.session(python=("3.12"), venv_backend="none")
    def dockerRemakeDocs(session):
        """Regenerate the documentation using Sphinx through docker (cleans up old docs)."""
        session.run("docker", "exec", "-it", "hm_web_image", "toc", "-s", "remakeDocs")


    @nox.session(python=("3.12"), venv_backend="none")
    def dockerLogs(session):
        """Output docker logs out to console. (hit <ctrl>c to stop)."""
        session.run("docker", "compose", "logs", "--follow")


    @nox.session(python=("3.12"), venv_backend="none")
    def dockerTesting(session):
        """Run automated tests (localtest) through docker."""
        session.run("docker", "exec", "-it", "hm_web_image", "nox", "-s", "testing")



    ##################################################################################
    # To Do: Other Local Tasks


    @nox.session(python=("3.12"), venv_backend="none")
    def ruff(session):
        """ run the ruff code standards tool """
        with Path.open("./docs/qa/ruff_run.txt", "w") as out:
            session.run("ruff", "check", stdout=out) # optional parameter: "--fix")

    @nox.session(python=("3.12"), venv_backend="none")
    def mypy(session):
        """ run the mypy type checker """
        with Path.open("./docs/qa/mypy_run.txt", "w") as out:
            session.run("mypy",
                "./healthymeals",
                "--xslt-html-report",
                "./docs/qa/mypy/",
                stdout=out,
            )

    @nox.session(python=("3.12"), venv_backend="none")
    def flake8(session):
        """ run the flake8 code standards tool """
        with Path.open("./docs/qa/flake8_run.txt", "w") as out:
            session.run(
                "flake8",
                "./healthymeals",
                "--exit-zero",
                "--format=html",
                "--htmldir=./docs/qa/flake8/html",
                "--statistics",
                "--tee",
                "--output-file",
                "./docs/qa/flake8/flake8stats.txt",
                "--config=setup.cfg",
                "--select=E251",
                stdout=out,
            ) # run flake8 tool
            session.run("genbadge", "flake8",
                "--input-file", "./docs/qa/flake8/flake8stats.txt",
                "--output-file", "./docs/qa/flake8/flake8_badge.svg",
                stdout=out,
            ) # create coverage badge

    # @nox.session(python=("3.12"), venv_backend="none")  # noqa: ERA001
    # def djlint(session):  # noqa: ERA001
    #     """ run the djlint code standards tool """  # noqa: ERA001
    #     with Path.open("./docs/qa/djlint_run.txt", "w") as out:
    #         session.run("djlint", "./healthymeals")  # noqa: ERA001

    # @nox.session(python=("3.12"), venv_backend="none")  # noqa: ERA001
    # def pylint(session):  # noqa: ERA001
    #     """ run the pylint code standards tool """  # noqa: ERA001
    #     with Path.open("./docs/qa/pylint_run.txt", "w") as out:
    #         session.run("pylint", "./healthymeals")  # noqa: ERA001
