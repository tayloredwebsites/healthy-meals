from pathlib import Path
import os
import nox
import subprocess


##################################################################################
# Local Server tasks


@nox.session(python=("3.12"), venv_backend="none")
def setupEnv(session):
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




@nox.session(python=("3.12"), venv_backend="none")
def goodToGo(session):
    ''' Check to confirm that all is good to go (for push / commit / etc.).'''
    session.run("uv", "run", "nox", "-s", "setupEnv") # make sure session is set up if needed
    session.run("uv", "run", "nox", "-s", "sphinxDocs") # generate docs locally
    # session.run("uv", "run", "nox", "-s", "test_coverage") # already run in sphinxDocs
    '''Todo prevent commits until goodToGo runs and recreates dev-requirements.txt (??)'''
    # session.run("uv", "export", "--no-hashes", "--output-file", "dev-requirements.txt", "--group", "dev") #  --no-header --no-annotate --no-dev


@nox.session(python=("3.12"), venv_backend="none")
def localUp(session):
    ''' Bring up Healthy Meals in local server.'''
    session.run("uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000")


@nox.session(python=("3.12"), venv_backend="none")
def genNoxDocs(session):
    ''' Generate nox documentation into a file for inclusion into Sphinx.'''
    with Path.open("./docs/qa/nox_docs.txt", "w") as out:
        session.run("uv", "run", "nox", "--list",
            stdout=out, # output to nox_docs.txt
        )


@nox.session(python=("3.12"), venv_backend="none")
def sphinxDocs(session):
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


@nox.session(python=("3.12"), venv_backend="none")
def cleanTestsBuild(session):
    """Clean out docs/build directories for running tests and coverage"""
   # empty out only the tests and coverage directories in the doc/build directory
    session.run("uv", "run", "rm", "-fr", "./docs/build/tests")
    session.run("uv", "run", "rm", "-fr", "./docs/build/coverage")
    session.run("uv", "run", "rm", "-fr", "./docs/build/coverage_py")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage_py/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/tests/")


@nox.session(python=("3.12"), venv_backend="none")
def cleanDocsBuild(session):
    """Clean out docs/build directories for running tests and coverage"""
    # empty out and rebuild the entire docs/build directory
    session.run("uv", "run", "rm", "-fr", "./docs/build")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/coverage_py/html/")
    session.run("uv", "run", "mkdir", "-p", "./docs/build/tests/")
    # Note: documentation generated folder are written to by both sphinx and automated testing
    session.run("uv", "run", "rm", "-fr", "./docs/source")
    session.run("uv", "run", "mkdir", "-p", "./docs/source/")
    session.run("uv", "run", "cp", "-R", "./docs/sphinx_src/", "./docs/source/")


@nox.session(python=("3.12"), venv_backend="none")
def testing(session):
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



@nox.session(python=("3.12"), venv_backend="none")
def testing_debug(session):
    """Run all automated tests with expanded debugging statements."""
    # empty out docs, tests, and coverage directories in docs/build
    session.run("uv", "run", "nox", "-s", "cleanTestsBuild")

    session.run("uv", "run", "pytest", "tests",
        "-s", # output print statements
        "--log-cli-level=debug", # output debug statements
    ) # run tests with debugging output


@nox.session(python=("3.12"), venv_backend="none")
def testing_cov(session):
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


@nox.session(python=("3.12"), venv_backend="none")
def testing_final(session):
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
    '''to Only bring up Healthy Meals in docker if not up already.'''
    session.run("docker", "compose", "up", "--build", "--detach", "--no-recreate")


@nox.session(python=("3.12"), venv_backend="none")
def dockerExecSh(session):
    '''to Open shell in web container.'''
    session.run("docker", "exec", "-it", "healthy-meals-web-1", "sh")


@nox.session(python=("3.12"), venv_backend="none")
def dockerExecPsql(session):
    '''to Open psql in db container.'''
    session.run("docker", "exec", "-it", "healthy-meals-pg_db-1", "psql", "--dbname=healthy_meals", "--username=healthy_meals")


@nox.session(python=("3.12"), venv_backend="none")
def dockerDown(session):
    '''Bring down all Healthy Meals Docker Containers

    We get the active docker procs that are wild card filtered to match the names of all healthy-meal containers
    a pipe is used to pass the container ids between the docker ps command and the docker stop command
    xargs is used to feed the container ids into docker stop command as arguments
    '''
    # session.run("docker", "stop", "healthy-meals-web-1")
    # session.run("docker", "stop", "healthy_meals-pg_db-1")
    session.run("bash", "-c", "docker ps -q --filter 'name=healthy-meals*' | xargs docker stop")


@nox.session(python=("3.12"), venv_backend="none")
def dockerSphinxDocs(session):
    """to Generate the documentation using Sphinx through docker.

    Note: Requires healthy-meals docker container to be running
    """
    session.run("docker", "exec", "-it", "healthy-meals-web-1", "nox", "-s", "sphinxDocs")


@nox.session(python=("3.12"), venv_backend="none")
def dockerLogs(session):
    """to Output docker logs out to console. (hit <ctrl>c to stop)."""
    session.run("docker", "compose", "logs", "--follow")


@nox.session(python=("3.12"), venv_backend="none")
def dockerTesting(session):
    """to Run automated tests (localtest) through docker.

    Note: Requires healthy-meals docker container to be running
    """
    session.run("docker", "exec", "-it", "healthy-meals-web-1", "nox", "-s", "test_coverage")



##################################################################################
# To Do: Other QA Tasks

@nox.session(python=("3.12"), venv_backend="none")
def mypy(session):
    with Path.open("./docs/qa/mypy_run.txt", "w") as out:
        session.run("mypy",
            "./healthymeals",
            "--xslt-html-report",
            "./docs/qa/mypy/",
            stdout=out,
        )


@nox.session(python=("3.12"), venv_backend="none")
def ruff(session):
    with Path.open("./docs/qa/ruff_run.txt", "w") as out:
        session.run("ruff", "check", stdout=out) # optional parameter: "--fix")


@nox.session(python=("3.12"), venv_backend="none")
def flake8(session):
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


@nox.session(python=("3.12"), venv_backend="none")
def djlint(session):
   with Path.open("./docs/qa/djlint_run.txt", "w") as out:
        session.run("djlint", "./healthymeals")

@nox.session(python=("3.12"), venv_backend="none")
def pylint(session):
    with Path.open("./docs/qa/pylint_run.txt", "w") as out:
        session.run("pylint", "./healthymeals")
