
from subprocess import run
import pytest

# from .factories import CustomUserFactory

# from accounts.models import CustomUser

# from django.db import IntegrityError, transaction

@pytest.mark.slow
def test_docker_bg_run():
    '''Ensure docker runs in background

    Steps:
        - confirm the docker containers are both down
        - Start by running docker in the background
        - confirm they are both up
        - run the ensure up, and confirm they are both still up.
        - do a curl command and confirm it has some correct text in it
        - run the docker sphinx docs command
        - run the docker testing command
        - start the docker web console and exit it immediately
        - start the docker psql console aand exit it immediately
        - run the docker down command, and confirm they are both down
        - analysis of any other steps that could be tested
    '''

    # show starting message
    print('Starting tests/nox/test_local_nox.py::test_docker_bg_run')
    ret = run(["nox", "-s", "dockerUpBg"])
    assert ret.returncode == 0
