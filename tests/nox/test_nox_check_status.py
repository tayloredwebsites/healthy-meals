'''tests/nox/test_nox_check_status.py

unit tests for noxfile.py checkStatus script
- using pytest-git: https://github.com/man-group/pytest-plugins/tree/master/pytest-git
- for good example of GitPytest testing see: https://stackoverflow.com/questions/32381251/how-to-write-unit-tests-for-gitpython-clone-pull-functions#answer-77245403
- we are using the class git_info.py::GitInfo to collect information about the repo
'''
import pytest
import os
import shutil
import git # https://gitpython.readthedocs.io/en/stable/index.html
import typing
from pathlib import Path

from hm_utils.git_info import GitInfo

import logging
logger = logging.getLogger(__name__)

'''Setup run before every test method.

.. ToDo: test_nox_check_status.py: replace TMP_GIT_REPO_DIR with pytest tmp_path fixture
'''

def test_chkstat_clean(setUpAndDown, tmp_path, conftest_constants):
    '''make sure that all is reported as good when the git repo is clean (unchanged).

    Args:
        setUpAndDown mixin: a pytest fixture to create a gitpython (git) Repo to test against
        conftest_constants mixin: shared testing constants from tests/conftest.py
        tmp_path fixture: temporary path. see: https://docs.pytest.org/en/7.1.x/how-to/tmp_path.html#tmp-path-handling

    '''

    logger = logging.getLogger(__name__)

    # show starting message
    print('**************************************************************************************')
    print('test_nox_check_status: Starting tests/nox/test_nox_check_status.py::test_chkstat_clean')

    # obtain setup data
    repo = setUpAndDown

    logger.debug(f'test_chkstat_clean tmp_path @ {tmp_path}')
    logger.debug(f'test_chkstat_clean tmp_path @ {tmp_path}')
    logger.debug(f'test_chkstat_clean repo directory: {os.listdir(Path(conftest_constants['TMP_GIT_REPO_DIR']))}')

    num_mods = len(repo.git.diff(None))
    logger.info(f'test_chkstat_clean num_mods: {num_mods}')

    # # create a GitInfo instance (git_info) to extract and store the information about the git repo
    # git_info = GitInfo(repo, 'git@github.com:tayloredwebsites/healthy-meals.git', 'https://github.com/tayloredwebsites/healthy-meals', '') # '5ce0869c5967646a011bc5169e8135303f537a5e')
    # git_info = GitInfo(repo, config('TEST_UPSTREAM_GIT'), config('TEST_UPSTREAM_REPO_URL'), config(''))

    # # validate the git repo
    # logger.debug(f'test_chkstat_clean git_info num_mods: {len(git_info.repo.git.diff(None))}')
    # assert git_info.num_mods == 0, 'number of modified files is not 0'
    # assert git_info.num_untracked == 0, 'number of untracked files is not 0'
    # assert git_info.num_staged == 0, 'number of staged files is not 0'
    # logger.debug(f'test_chkstat_clean git_info.num_updates: {git_info.num_updates}')
    # assert git_info.num_updates == 0, 'number of updated files is not 0'

def test_tmp_path(tmp_path):
    logger.debug(f'test_tmp_path tmp_path @ {tmp_path}')
    logger.debug(f'test_tmp_path tmp_path @ {tmp_path}')
    # confirm tmp_path doesn't change within a test
    assert tmp_path == tmp_path

############################################ pytest fixtures ######################################

@pytest.fixture
def setUpAndDown(conftest_constants):
    logger.debug('set up using setUpAndDown of test_nox_check_status.py')

    # delete git repo file if it exists
    # cannot run tests in parallel with this coding
    try:
        shutil.rmtree(conftest_constants['TMP_GIT_REPO_DIR'])
    except:
        if os.path.isdir(conftest_constants['TMP_GIT_REPO_DIR']):
            print(f'Unable to remove directory: {conftest_constants['TMP_GIT_REPO_DIR']}')
            quit()

    # create the temporary repo
    repo = git.Repo.init(Path(conftest_constants['TMP_GIT_REPO_DIR']))
    logger.debug(f'created repo @ {os.listdir(Path(conftest_constants['TMP_GIT_REPO_DIR']))}')

    # create a file, and do first commit
    app_file_name = Path(conftest_constants['TMP_GIT_REPO_DIR']) / 'initial_file'
    open(app_file_name, 'w').close()
    logger.debug(f'added to repo @ {os.listdir(Path(conftest_constants['TMP_GIT_REPO_DIR']))}')

    repo.index.add(['initial_file'])
    repo.index.commit("initial commit")
    # repo.remote("origin").push()

    num_mods = len(repo.git.diff(None))
    num_untracked = len(repo.untracked_files)
    num_staged = len(repo.index.diff("HEAD"))
    num_updates = num_mods + num_untracked + num_staged
    any_updates = True if num_updates > 0 else False

    logger.debug(f'any_updates: {any_updates}')
    if any_updates:
        logger.debug(f'num_mods: {num_mods}, num_untracked: {num_untracked}, num_staged: {num_staged}')

    data: Tuple[git.Repo] = (repo)

    # yield to tests, passing data to them
    yield data

    logger.debug('tear down of setUpAndDown of test_nox_check_status.py')
    # delete git repo file if it exists
    # cannot run tests in parallel with this coding
    try:
        shutil.rmtree(conftest_constants['TMP_GIT_REPO_DIR'])
    except:
        if os.path.isdir(conftest_constants['TMP_GIT_REPO_DIR']):
            print(f'Unable to remove directory: {conftest_constants['TMP_GIT_REPO_DIR']}')
            quit()

    logger.error('removed repo')
