'''
Healthy Meals Web Site
Copyright (C) 2025 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals - accounts/models.py
'''
from pathlib import Path
import os
import nox
import subprocess

import logging

'''uv integrations with nox

see: https://edward-jazzhands.github.io/posts/python-testing-with-nox-and-uv/
'''
# PYTHON_VERSIONS = ["3.12"] # list of session names includes version. e.g. setupEnv-3.12
PYTHON_VERSIONS = "3.12" # list of session names does not include version. e.g. setupEnv



##################################################################################
# Local Server tasks


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def setupEnv(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    '''Set up external environment as needed (no venv)).'''
    # empty out tests and coverage directories
    session.run("uv", "run", "nox", "-s", "cleanDocsBuild")
    # Make sure that the database is fully migrated before proceeding
    session.run("uv", "run", "python", "manage.py", "makemigrations")
    session.run("uv", "run", "python", "manage.py", "migrate")
    # convert all SCSS files to CSS
    session.run("uv", "run","sass", "static/scss:static/css")
    # collect all static files to be deployed to the website
    session.run("uv", "run", "python", "manage.py", "collectstatic", "--noinput")
    # session.run("uv", "run", "rm", "-f", "dev-requirements.txt")
    session.run("uv", "run", "ls", "-al", "./docs/source/") # confirm docs source directory exists


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def goodToGo(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    ''' Check to confirm that all is good to go (for push / commit / etc.).'''
    session.run("uv", "run", "nox", "-s", "setupEnv") # make sure session is set up if needed
    session.run("uv", "run", "nox", "-s", "sphinxDocs") # generate docs locally
    # session.run("uv", "run", "nox", "-s", "test_coverage") # already run in sphinxDocs
    '''Todo prevent commits until goodToGo runs and recreates dev-requirements.txt (??)'''
    # session.run("uv", "export", "--no-hashes", "--output-file", "dev-requirements.txt", "--group", "dev") #  --no-header --no-annotate --no-dev


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def localUp(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    ''' Bring up Healthy Meals in local server.'''
    session.run("uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000")


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def genNoxDocs(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    ''' Generate nox documentation into a file for inclusion into Sphinx.'''
    with Path.open("./docs/qa/nox_docs.txt", "w") as out:
        session.run("uv", "run", "nox", "--list",
            stdout=out, # output to nox_docs.txt
        )


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def sphinxDocs(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    """Rebuild all documentation to Sphinx (cleans up old docs).

    Ignore the warning about modules.rst not included in the toctree,
    as modules are manually entered into index.rst

    """
    # empty out and rebuild the entire docs/build directory
    session.run("uv", "run", "nox", "-s", "cleanDocsBuild")
    session.run("uv", "run", "nox", "-s", "testing_final")
    session.run("uv", "run", "nox", "-s", "genNoxDocs")
    session.run("uv", "run", "make", "apidocs", "--directory=docs")
    session.run("uv", "run", "ls", "-al", "./docs/source/") # confirm docs source directory exists
    session.run("uv", "run", "make", "allhtml", "--directory=docs")


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def cleanTestsBuild(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    """Clean out docs/build directories for running tests and coverage"""
   # empty out only the tests and coverage directories in the doc/build directory
    session.run("uv", "run", "rm", "-fr", "./docs/build/tests")
    session.run("uv", "run", "rm", "-fr", "./docs/build/coverage")
    session.run("uv", "run", "rm", "-fr", "./docs/build/coverage_py")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage_py/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/tests/")


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def cleanDocsBuild(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    """Clean out docs/build directories for running tests and coverage"""
    # empty out and rebuild the entire docs/build directory
    session.run("uv", "run", "rm", "-fr", "./docs/build")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage_py/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/tests/")
    # Note: documentation generated folder are written to by both sphinx and automated testing
    session.run("uv", "run", "rm", "-fr", "./docs/source")
    # session.run("uv", "run", "mkdir", "-p", "./docs/source/")
    session.run("uv", "run", "cp", "-R", "./docs/sphinx_src/", "./docs/source/")


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def testing(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    """Run condensed output automated tests)."""

    logger = logging.getLogger(__name__)

    # empty out docs, tests, and coverage directories in docs/build
    session.run("uv", "run", "nox", "-s", "cleanTestsBuild")

    try:
        session.run("uv", "run", "pytest", "tests",
            "--tb=no", # output no debugging statements on error
            "--log-cli-level=INFO", # do not output debug statements
        ) # run tests with debugging output
    except Exception as ex:
        print(f'''pytest Automated Testing failure: {ex}
        To run an individual failed test, copy the filename in beginning of the FAILED message (aka <filename>)
        To run an individual test, run the following command in the command line:
            uv run pytest <filename>
        ''')
    
    logging.disable(logging.NOTSET)



@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def testing_debug(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    """Run all automated tests with expanded debugging statements."""
    # empty out docs, tests, and coverage directories in docs/build
    session.run("uv", "run", "nox", "-s", "cleanTestsBuild")

    session.run("uv", "run", "pytest", "tests",
        "-s", # output print statements
        "--log-cli-level=debug", # output debug statements
    ) # run tests with debugging output


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def testing_cov(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    """Run condensed output automated tests with coverage reports."""
    # empty out docs, tests, and coverage directories in docs/build
    session.run("uv", "run", "nox", "-s", "cleanTestsBuild")

    session.run("uv", "run", "coverage", "run", "-m", "pytest", "tests",
        "--junitxml=./docs/build/tests/junit.xml",
        "--html=./docs/build/tests/index.html",
        "--tb=short", # output debug statements: https://docs.pytest.org/en/7.1.x/how-to/output.html
        # not logging: stdout=out, # output to ran_coverage.txt
    ) # run tests with coverage
    session.run("uv", "run", "coverage", "xml",
        "-o", "./docs/build/coverage/coverage.xml", # xml output file
        # not logging: stdout=out, # output to ran_coverage.txt
    ) # create coverage.xml file
    session.run("uv", "run", "coverage", "html",
        "-d", "./docs/build/coverage/html/", # html output directory
        # not logging: stdout=out, # output to ran_coverage.txt
    ) # create coverage HTML files
    session.run("uv", "run", "coverage", "xml", "--omit=*.html,*.txt",
        "-o", "./docs/build/coverage_py/coverage.xml", # xml output file
        # not logging: stdout=out, # output to ran_coverage.txt
    ) # create python only coverage.xml file
    session.run("uv", "run", "coverage", "html", "--omit=*.html,*.txt",
        "-d", "./docs/build/coverage_py/html/", # html output directory
        # not logging: stdout=out, # output to ran_coverage.txt
    ) # create python only coverage HTML files


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def testing_final(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    """Run final automated tests and coverage reports with output to coverage_run.txt file."""
    with Path.open("./docs/build/coverage_run.txt", "w") as out:

        # empty out docs, tests, and coverage directories in docs/build
        session.run("uv", "run", "nox", "-s", "cleanTestsBuild")

        session.run("uv", "run", "coverage", "run", "-m", "pytest", "tests",
            "--junitxml=./docs/build/tests/junit.xml",
            "--html=./docs/build/tests/index.html",
            stdout=out, # output to coverage_run.txt
        ) # run tests with coverage
        session.run("uv", "run", "genbadge", "tests",
            "--input-file", "./docs/build/tests/junit.xml",
            "--output-file", "./docs/build/tests/tests_badge.svg",
            stdout=out, # output to coverage_run.txt
        ) # create tests badge
        session.run("uv", "run", "coverage", "xml",
            "-o", "./docs/build/coverage/coverage.xml", # xml output file
            stdout=out, # output to coverage_run.txt
        ) # create coverage.xml file
        session.run("uv", "run", "coverage", "html",
            "-d", "./docs/build/coverage/html/", # html output directory
            stdout=out, # output to coverage_run.txt
        ) # create coverage HTML files
        session.run("uv", "run", "genbadge", "coverage", "--name", "total coverage",
            "--input-file", "./docs/build/coverage/coverage.xml",
            "--output-file", "./docs/build/coverage/coverage_badge.svg",
            stdout=out, # output to coverage_run.txt
        ) # create coverage badge
        session.run("uv", "run", "coverage", "xml", "--omit=*.html,*.txt",
            "-o", "./docs/build/coverage_py/coverage.xml", # xml output file
            stdout=out, # output to coverage_run.txt
        ) # create python only coverage.xml file
        session.run("uv", "run", "coverage", "html", "--omit=*.html,*.txt",
            "-d", "./docs/build/coverage_py/html/", # html output directory
            stdout=out, # output to coverage_run.txt
        ) # create python only coverage HTML files
        session.run("uv", "run", "genbadge", "coverage", "--name", "python coverage",
            "--input-file", "./docs/build/coverage_py/coverage.xml",
            "--output-file", "./docs/build/coverage_py/coverage_badge.svg",
            stdout=out, # output to coverage_run.txt
        ) # create coverage badge


##################################################################################
# Docker tasks

@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def dockerUpBg(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    '''Bring up Healthy Meals in docker in background.'''
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerUpBg - started')
    session.run("docker", "compose", "up", "--build", "--detach")
    logger.debug(f'*** nox -s dockerUpBg - done')


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def dockerUpLog(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    '''Bring up Healthy Meals in docker, with log to console.'''
    session.run("docker", "compose", "up", "--build")


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def dockerEnsureUp(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    '''bring up Healthy Meals in docker (in background) if not up already.'''
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerEnsureUp - started')
    session.run("docker", "compose", "up", "--build", "--detach", "--no-recreate")
    logger.debug(f'*** nox -s dockerEnsureUp - done')


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def dockerExecSh(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    '''to Open shell in web container, need to type "exit" to shut it down'''
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerExecSh - started')
    session.run("docker", "exec", "-it", "healthy-meals-web-1", "sh")
    logger.debug(f'*** nox -s dockerExecSh - done')


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def dockerExecPsql(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    '''to Open psql in db container, need to type \\q to shut it down.'''
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerExecPsql - started')
    session.run("docker", "exec", "-it", "healthy-meals-pg_db-1", "psql", "--dbname=healthy_meals", "--username=healthy_meals")
    logger.debug(f'*** nox -s dockerExecPsql - done')


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def dockerDown(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    '''Bring down all Healthy Meals Docker Containers

    We get the active docker procs that are wild card filtered to match the names of all healthy-meal containers
    a pipe is used to pass the container ids between the docker ps command and the docker stop command
    xargs is used to feed the container ids into docker stop command as arguments
    '''
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerDown - started')
    # session.run("docker", "stop", "healthy-meals-web-1")
    # session.run("docker", "stop", "healthy_meals-pg_db-1")
    session.run("bash", "-c", "docker ps -q --filter 'name=healthy-meals*' | xargs docker stop")
    logger.debug(f'*** nox -s dockerDown - done')


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def dockerSphinxDocs(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    """to Generate the documentation using Sphinx through docker.

    Note: Requires healthy-meals docker container to be running
    """
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerSphinxDocs - started')
    session.run("docker", "exec", "-it", "healthy-meals-web-1", "nox", "-s", "sphinxDocs")
    logger.debug(f'*** nox -s dockerSphinxDocs - done')


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def dockerLogs(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    """to Output docker logs out to console. (hit <ctrl>c to stop)."""
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerLogs - started')
    session.run("docker", "compose", "logs", "--follow")
    logger.debug(f'*** nox -s dockerLogs - done')


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def dockerTesting(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    """to Run automated tests (localtest) through docker.

    Note: Requires healthy-meals docker container to be running
    """
    logger = logging.getLogger(__name__)
    logger.debug(f'*** nox -s dockerTesting - started')
    session.run("docker", "exec", "-it", "healthy-meals-web-1", "nox", "-s", "testing")
    logger.debug(f'*** nox -s dockerTesting - done')



##################################################################################
# To Do: Other QA Tasks

@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def mypy(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    with Path.open("./docs/qa/mypy_run.txt", "w") as out:
        session.run("mypy",
            "./healthymeals",
            "--xslt-html-report",
            "./docs/qa/mypy/",
            stdout=out,
        )


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def ruff(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    with Path.open("./docs/qa/ruff_run.txt", "w") as out:
        session.run("ruff", "check", stdout=out) # optional parameter: "--fix")


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def flake8(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
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


@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def djlint(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    with Path.open("./docs/qa/djlint_run.txt", "w") as out:
        session.run("djlint", "./healthymeals")

@nox.session(venv_backend="uv", python=PYTHON_VERSIONS)
def pylint(session: nox.Session) -> None:
    session.run_install("uv", "sync", "--quiet",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    with Path.open("./docs/qa/pylint_run.txt", "w") as out:
        session.run("pylint", "./healthymeals")
