#!/usr/bin/env -S uv run --script --quiet

# noinspection PyPep8Naming  # to allow nox script names to be camelcase for easier typing in terminal

# /// script
# dependencies = ["nox", "nox-uv"]
# ///
"""
Healthy Meals Web Site
Copyright (C) 2025 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals - accounts/models.py
"""

from pathlib import Path
import nox
import logging

PYTHON_VERSION = "3.12"


########################################################################################################################
# Developer scripts/sessions for local server
########################################################################################################################


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def localUp(session: nox.Session):
    """Bring up Healthy Meals in local server."""
    session.run_install("uv", "sync", "--quiet", external=True, )
    session.run("uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000")


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def testing(session):
    """Run condensed output automated tests)."""
    session.run_install("uv", "sync", "--quiet", external=True, )
    # empty out docs, tests, and coverage directories in docs/build
    session.run("uv", "run", "nox", "-s", "cleanTestsBuild")
    try:
        session.run("uv", "run", "pytest", "tests",
                    "--tb=no",  # output no debugging statements on error
                    "--log-cli-level=INFO",  # do not output debug statements
                    )  # noqa: E128 # run tests with debugging output
    except Exception as ex:
        print(f'''pytest Automated Testing failure: {ex}
        To run an individual failed test:
            - copy the filename in beginning of the FAILED message (aka <filename>)
            - run the following command in the command line:
                uv run pytest -s <filename>
        To run all tests in debug mode:
                uv run nox -s testingDebug
        ''')


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def testingDebug(session):
    """Run all automated tests with expanded debugging statements."""
    session.run_install("uv", "sync", "--quiet", external=True, )
    # empty out docs, tests, and coverage directories in docs/build
    session.run("uv", "run", "nox", "-s", "cleanTestsBuild")

    session.run("uv", "run", "pytest", "tests",
                "-s",  # output print statements
                "--log-cli-level=debug",  # output debug statements
                )  # noqa: E128 # run tests with debugging output


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def sphinxDocs(session):
    """Run sphinx docs without running testing and coverage reporting"""
    session.run_install("uv", "sync", "--quiet", external=True, )
    try:
        with Path.open('./docs/qa/nox_sphinx_log.txt', "w") as out:
            session.run(
                "uv", "run", "nox", "-s", "setupEnv",
                stdout=out,  # output to nox_sphinx_log.txt
            )  # noqa: E128 # split shell commands read better
            session.run(
                "uv", "run", "nox", "-s", "onlySphinxDocs",
                stdout=out,  # output to nox_sphinx_log.txt
            )  # noqa: E128 # split shell commands read better
    except Exception as ex:
        print(f'''pytest Good To Go failure: {ex}
        This code is not ready for a pull request merge.
            - the CI (Continuous Integration) will fail when running djangoUvCi, which runs this check
        ''')
    print(f'''To see the output of the nox sessions, run the following command in the command line:
        cat docs/qa/nox_sphinx_log.txt''')

    """.. todo:: prevent commits until goodToGo runs - consider requiring dev-requirements.txt to exist to do a commit?"""
    # session.run("uv", "export", "--no-hashes", "--output-file", "dev-requirements.txt", "--group", "dev") #  --no-header --no-annotate --no-dev


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def allDocs(session):
    """Run sphinx docs without running testing and coverage reporting"""
    session.run_install("uv", "sync", "--quiet", external=True, )
    try:
        with Path.open('./docs/qa/nox_sphinx_log.txt', "w") as out:
            session.run(
                "uv", "run", "nox", "-s", "setupEnv",
                stdout=out,  # output to nox_sphinx_log.txt
            )  # noqa: E128 # split shell commands read better
            session.run(
                "uv", "run", "nox", "-s", "coverageReports",
                stdout=out,  # output to nox_go_log.txt
            )  # noqa: E128 # split shell commands read better
            session.run(
                "uv", "run", "nox", "-s", "onlySphinxDocs",
                stdout=out,  # output to nox_sphinx_log.txt
            )  # noqa: E128 # split shell commands read better
    except Exception as ex:
        print(f'''pytest Good To Go failure: {ex}
        This code is not ready for a pull request merge.
            - the CI (Continuous Integration) will fail when running djangoUvCi, which runs this check
        ''')
    print(f'''To see the output of the nox sessions, run the following command in the command line:
        cat docs/qa/nox_sphinx_log.txt''')

    """.. todo:: prevent commits until goodToGo runs - consider requiring dev-requirements.txt to exist to do a commit?"""
    # session.run("uv", "export", "--no-hashes", "--output-file", "dev-requirements.txt", "--group", "dev") #  --no-header --no-annotate --no-dev


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def goodToGo(session):
    """Check to confirm that all is good to go (for push / commit / etc.)."""
    session.run_install("uv", "sync", "--quiet", external=True, )
    try:
        with Path.open('./docs/qa/nox_go_log.txt', "w") as out:
            session.run(
                "uv", "run", "nox", "-s", "setupEnv",
                stdout=out,  # output to nox_go_log.txt
            )  # noqa: E128 # split shell commands read better
            session.run(
                "uv", "run", "nox", "-s", "testing",
                stdout=out,  # output to nox_go_log.txt
            )  # noqa: E128 # split shell commands read better
            session.run(
                "uv", "run", "nox", "-s", "coverageReports",
                stdout=out,  # output to nox_go_log.txt
            )  # noqa: E128 # split shell commands read better
            session.run(
                "uv", "run", "nox", "-s", "onlySphinxDocs",
                stdout=out,  # output to nox_go_log.txt
            )  # noqa: E128 # split shell commands read better
    except Exception as ex:
        print(f'''pytest Good To Go failure: {ex}
        This code is not ready for a pull request merge.
            - the CI (Continuous Integration) will fail when running djangoUvCi, which runs this check
        ''')
    print(f'''To see the output of the nox sessions, run the following command in the command line:
        cat docs/qa/nox_go_log.txt''')

    """.. todo:: prevent commits until goodToGo runs - consider requiring dev-requirements.txt to exist to do a commit?"""
    # session.run("uv", "export", "--no-hashes", "--output-file", "dev-requirements.txt", "--group", "dev") #  --no-header --no-annotate --no-dev


########################################################################################################################
# Developer scripts/sessions for Docker
########################################################################################################################


# Docker tasks

@nox.session(python=PYTHON_VERSION, venv_backend="none")
def dockerUpBg(session):
    session.skip('todo:: debug nox dockerUpBg')
    """.. todo:: debug nox dockerUpBg - Bring up Healthy Meals in docker in background.

        - docker run through nox need errors:
        - dockerUpBg returns error: relation "django_site" does not exist"

    """
    session.run_install("uv", "sync", "--quiet", external=True, )
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerUpBg - started')
    session.run("docker", "compose", "up", "--build", "--detach")
    logger.debug(f'*** nox -s dockerUpBg - done')


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def dockerUpLog(session):
    session.skip('todo:: debug nox dockerUpLog')
    """.. todo:: debug nox dockerUpLog - Bring up Healthy Meals in docker, with log to console."""
    session.run_install("uv", "sync", "--quiet", external=True, )
    session.run("docker", "compose", "up", "--build")


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def dockerEnsureUp(session):
    session.skip('todo:: debug nox dockerEnsureUp')
    """.. todo:: debug nox dockerEnsureUp - bring up Healthy Meals in docker (in background) if not up already."""
    session.run_install("uv", "sync", "--quiet", external=True, )
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerEnsureUp - started')
    session.run("docker", "compose", "up", "--build", "--detach", "--no-recreate")
    logger.debug(f'*** nox -s dockerEnsureUp - done')


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def dockerExecSh(session):
    session.skip('todo:: debug nox dockerExecSh')
    """.. todo:: debug nox dockerExecSh - to Open shell in web container, need to type "exit" to shut it down"""
    session.run_install("uv", "sync", "--quiet", external=True, )
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerExecSh - started')
    session.run("docker", "exec", "-it", "healthy-meals-web-1", "sh")
    logger.debug(f'*** nox -s dockerExecSh - done')


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def dockerExecPsql(session):
    session.skip('todo:: debug nox dockerExecPsql')
    """.. todo:: debug nox dockerExecPsql - to Open psql in db container, need to type \\q to shut it down."""
    session.run_install("uv", "sync", "--quiet", external=True, )
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerExecPsql - started')
    session.run("docker", "exec", "-it", "healthy-meals-pg_db-1", "psql", "--dbname=healthy_meals",
                "--username=healthy_meals")  # noqa: E128
    logger.debug(f'*** nox -s dockerExecPsql - done')


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def dockerDown(session):
    session.skip('todo:: debug nox dockerDown')
    """.. todo:: debug nox dockerDown - Bring down all Healthy Meals Docker Containers

        We get the active docker procs that are wild card filtered to match the names of all healthy-meal containers
        a pipe is used to pass the container ids between the docker ps command and the docker stop command
        xargs is used to feed the container ids into docker stop command as arguments
    """
    session.run_install("uv", "sync", "--quiet", external=True, )
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerDown - started')
    # session.run("docker", "stop", "healthy-meals-web-1")
    # session.run("docker", "stop", "healthy_meals-pg_db-1")
    session.run("bash", "-c", "docker ps -q --filter 'name=healthy-meals*' | xargs docker stop")
    logger.debug(f'*** nox -s dockerDown - done')


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def dockerLogs(session):
    session.skip('todo:: debug nox dockerLogs')
    """.. todo:: debug nox dockerLogs - to Output docker logs out to console. (hit <ctrl>c to stop)."""
    session.run_install("uv", "sync", "--quiet", external=True, )
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerLogs - started')
    session.run("docker", "compose", "logs", "--follow")
    logger.debug(f'*** nox -s dockerLogs - done')


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def dockerTesting(session):
    session.skip('todo:: debug nox dockerTesting')
    """.. todo:: debug nox dockerTesting - to Run automated tests (localtest) through docker.

        Note: Requires healthy-meals docker container to be running
    """
    session.run_install("uv", "sync", "--quiet", external=True, )
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerTesting - started')
    session.run("docker", "exec", "-it", "healthy-meals-web-1", "nox", "-s", "testing")
    logger.debug(f'*** nox -s dockerTesting - done')


########################################################################################################################
# Support Functions
########################################################################################################################


# noinspection PyPep8Naming
# @nox_uv.session(python=PYTHON_VERSIONS) # venv_backend="uv",
@nox.session(python=PYTHON_VERSION, venv_backend="none")
def setupEnv(session: object) -> None:
    """(support function) Set up external environment as needed (no venv)."""
    # session.run_install("uv", "sync", "--quiet", external=True, )
    # empty out tests and coverage directories
    session.run("uv", "run", "nox", "-s", "cleanDocsBuild")
    # Make sure that the database is fully migrated before proceeding
    session.run("uv", "run", "python", "manage.py", "makemigrations")
    session.run("uv", "run", "python", "manage.py", "migrate")
    # convert all SCSS files to CSS
    session.run("uv", "run", "sass", "static/scss:static/css")
    # collect all static files to be deployed to the website
    session.run("uv", "run", "python", "manage.py", "collectstatic", "--noinput")
    # session.run("uv", "run", "rm", "-f", "dev-requirements.txt")  # todo prevent commit if errors
    session.run("uv", "run", "ls", "-al", "./docs/source/")  # confirm docs source dir was copied from sphinx_src


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def genNoxDocs(session: nox.Session):
    """(support function) Generate nox documentation into a file for inclusion into Sphinx."""
    # session.run_install("uv", "sync", "--quiet", external=True, )
    with Path.open('./docs/qa/nox_docs.txt', "w") as out:
        session.run("uv", "run", "nox", "--list")


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def onlySphinxDocs(session: nox.Session):
    """(support function) Rebuild all documentation to Sphinx (cleans up old docs).
    Ignore the warning about modules.rst not included in the toctree,
    as modules are manually entered into index.rst
    """
    # session.run_install("uv", "sync", "--quiet", external=True, )
    # empty out and rebuild the entire docs/build directory
    # session.run("uv", "run", "nox", "-s", "setupEnv")  # make sure session is set up if needed
    session.run("uv", "run", "nox", "-s", "genNoxDocs")
    session.run("uv", "run", "make", "apidocs", "--directory=docs")
    session.run("uv", "run", "ls", "-al", "./docs/source/")  # confirm docs source directory exists
    session.run("uv", "run", "make", "allhtml", "--directory=docs")


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def cleanTestsBuild(session):
    """(support function) Clean out docs/build directories for running tests and coverage, leaving sphinx docs alone"""
    # session.run_install("uv", "sync", "--quiet", external=True, )
    # empty out only the tests and coverage directories in the doc/build directory
    session.run("uv", "run", "rm", "-fr", "./docs/build/tests")
    session.run("uv", "run", "rm", "-fr", "./docs/build/coverage")
    session.run("uv", "run", "rm", "-fr", "./docs/build/coverage_py")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage_py/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/tests/")


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def cleanDocsBuild(session):
    """(support function) Clean out docs/build directories for running tests and coverage"""
    # session.run_install("uv", "sync", "--quiet", external=True, )
    # empty out and rebuild the entire docs/build directory
    session.run("uv", "run", "rm", "-fr", "./docs/build")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage_py/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/tests/")
    # Note: documentation generated folder are written to by both sphinx and automated testing
    session.run("uv", "run", "rm", "-fr", "./docs/source")
    # session.run("uv", "run", "mkdir", "-p", "./docs/source/")
    session.run("uv", "run", "cp", "-R", "./docs/sphinx_src/", "./docs/source/")


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def coverageReports(session):
    """(support function) Run condensed output automated tests with coverage reports."""
    # session.run_install("uv", "sync", "--quiet", external=True, )
    # # empty out docs, tests, and coverage directories in docs/build
    # session.run("uv", "run", "nox", "-s", "cleanTestsBuild")

    session.run("uv", "run", "coverage", "run", "-m", "pytest", "tests",
                "--junitxml=./docs/build/tests/junit.xml",
                "--html=./docs/build/tests/index.html",
                "--tb=short",  # output debug statements: https://docs.pytest.org/en/7.1.x/how-to/output.html
                # not logging: stdout=out, # output to ran_coverage.txt
                )  # noqa: E128 # run tests with coverage
    session.run("uv", "run", "coverage", "xml",
                "-o", "./docs/build/coverage/coverage.xml",  # xml output file
                # not logging: stdout=out, # output to ran_coverage.txt
                )  # noqa: E128 # create coverage.xml file
    session.run("uv", "run", "coverage", "html",
                "-d", "./docs/build/coverage/html/",  # html output directory
                # not logging: stdout=out, # output to ran_coverage.txt
                )  # noqa: E128 # create coverage HTML files
    session.run("uv", "run", "coverage", "xml", "--omit=*.html,*.txt",
                "-o", "./docs/build/coverage_py/coverage.xml",  # xml output file
                # not logging: stdout=out, # output to ran_coverage.txt
                )  # noqa: E128 # create python only coverage.xml file
    session.run("uv", "run", "coverage", "html", "--omit=*.html,*.txt",
                "-d", "./docs/build/coverage_py/html/",  # html output directory
                # not logging: stdout=out, # output to ran_coverage.txt
                )  # noqa: E128 # create python only coverage HTML files


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def dockerSphinxDocs(session):
    """(support function) to Generate the documentation using Sphinx through docker.

    Note: Requires healthy-meals docker container to be running
    """
    # session.run_install("uv", "sync", "--quiet", external=True, )
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerSphinxDocs - started')
    session.run("docker", "exec", "-it", "healthy-meals-web-1", "nox", "-s", "sphinxDocs")
    logger.debug(f'*** nox -s dockerSphinxDocs - done')


##################################################################################
# To Do: Other QA Tasks

@nox.session(python=PYTHON_VERSION, venv_backend="none")
def mypy(session):
    session.skip('todo:: debug nox mypy')
    """.. todo:: research getting nox mypy qa session working"""
    session.run_install("uv", "sync", "--quiet", external=True, )
    with Path.open("./docs/qa/mypy_run.txt", "w") as out:
        session.run(
            "mypy",
            "./healthymeals",
            "--xslt-html-report",
            "./docs/qa/mypy/",
            stdout=out,
        )


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def ruff(session):
    session.skip('todo:: debug nox ruff')
    """.. todo:: research getting nox ruff qa session working"""
    session.run_install("uv", "sync", "--quiet", external=True, )
    with Path.open("./docs/qa/ruff_run.txt", "w") as out:
        session.run("ruff", "check", stdout=out)  # noqa: E128  # optional parameter: "--fix")


# noqa: E128
@nox.session(python=PYTHON_VERSION, venv_backend="none")
def flake8(session):
    session.skip('todo:: debug nox flake8 (or ruff?)')
    """.. todo:: consider getting nox flake8 qa session working"""
    session.run_install("uv", "sync", "--quiet", external=True, )
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
        )  # run flake8 tool
        session.run(
            "genbadge",
            "flake8",
            "--input-file", "./docs/qa/flake8/flake8stats.txt",
            "--output-file", "./docs/qa/flake8/flake8_badge.svg",
            stdout=out,
        )  # create coverage badge


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def djlint(session):
    session.skip('todo:: debug nox djlint (or ruff?)')
    """.. todo:: consider getting nox djlint qa session working"""
    session.run_install("uv", "sync", "--quiet", external=True, )
    with Path.open("./docs/qa/djlint_run.txt", "w") as out:
        session.run("djlint", "./healthymeals")


@nox.session(python=PYTHON_VERSION, venv_backend="none")
def pylint(session):
    session.skip('todo:: debug nox pylint (or ruff?)')
    """.. todo:: consider getting nox pylint qa session working"""
    session.run_install("uv", "sync", "--quiet", external=True, )
    with Path.open("./docs/qa/pylint_run.txt", "w") as out:
        session.run("pylint", "./healthymeals")
