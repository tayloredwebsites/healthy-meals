
from subprocess import run
import pytest
import subprocess
from decouple import config

# from .factories import CustomUserFactory

# from accounts.models import CustomUser

# from django.db import IntegrityError, transaction

''' testing the nox docker scripts are time consuming, so we only run them with the runslow flag

We added the ability to mark tests with @pytest.mark.slow so they will only be run with the runslow flag
- by default tests marked as slow will be skipped unless the --runslow cli option is given in the command line
- see: https://docs.pytest.org/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option

Normal run examples:

  - Run all normal tests through nox:
    % nox -s testing 

  - Run all of the local tests (not in docker):
    % uv run pytest tests/nox/test_local_nox.py

Running long running tests (slow) examples:

  - Run all of the (long running) tests in this file:
    % uv run pytest --runslow tests/nox/test_docker_nox.py 
'''


# @pytest.mark.slow #
@pytest.mark.skip(reason="no need to test this, at this point")
def test_docker_running():
    '''Ensure docker container is running
    
    see: https://stackoverflow.com/questions/35586900/how-to-check-if-a-docker-instance-is-running#answer-35587211
    '''
    if not config('RUN_DOCKER_TESTS', default=False, cast=bool):
        pytest.skip("Not running Docker Tests")

    ret = subprocess.run(['docker', 'ps'])
    assert ret.returncode == 0, 'Docker is not running'


@pytest.mark.skip(reason="Is there any way to test this?")
@pytest.mark.slow
def test_nox_docker_scripts():
    '''Ensure nox docker scripts are working successfully'''

    if not config('RUN_DOCKER_TESTS', default=False, cast=bool):
        pytest.skip("Not running Docker Tests")

    print('***    Starting tests/nox/test_local_nox.py::test_docker_bg_run')

    print('*** 1 - confirm the docker containers are both down')

    # show starting message
    print('*** 2 - Start by running docker in the background (dockerUpBg)')
    ret = run(["nox", "-s", "dockerUpBg"])
    assert ret.returncode == 0, 'Error running dockerUpBg'

    print('*** 3 - confirm both docker containers are up')

    print('*** 4 - run the ensure up, and confirm they are both still up (dockerUpBg).')
    ret = run(["nox", "-s", "dockerEnsureUp"])
    assert ret.returncode == 0, 'Error running dockerEnsureUp'

    print('*** 5 - ??? do a curl command and confirm it has some correct text in it')

    print('*** 6 - open shell in web container (dockerExecSh).')
    ret = run(["nox", "-s", "dockerExecSh"])
    assert ret.returncode == 0, 'Error running dockerExecSh'

    print('*** 7 - exit the web container shell')
    ret = run(["echo", "exit()"])
    assert ret.returncode == 0, 'Error exiting dockerExecSh'

    print('*** 8 - open shell in database container (dockerExecPsql).')
    ret = run(["nox", "-s", "dockerExecPsql"])
    assert ret.returncode == 0, 'Error running dockerExecPsql'

    print('*** 9 - exit the database container shell')
    ret = run(["echo", "exit()"])
    assert ret.returncode == 0, 'Error exiting dockerExecPsql'

    print('*** 10 - run the docker down command, and confirm they are both down')

    print('*** 11 - run the docker testing command')

    print('*** 12 - run the docker dockerSphinxDocs command')

