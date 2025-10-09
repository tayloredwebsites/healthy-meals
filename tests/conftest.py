'''tests (root) conftest.py for configuration of all tests

- Custom pytest fixture @pytest.mark.slow (test is skipped unless --runslow cli option is given)
'''
import pytest

from pathlib import Path

@pytest.fixture()
def conftest_constants():
    '''fixture to hold testing constants

    .. todo::
        conftest.py
            - determine if conftest_constants is needed
            - remove TMP_BASE_DIR, and TMP_GIT_REPO_DIR after replacing with tmp_path in code
    '''
    return {
        # use pytest tmp_path fixture instead: https://docs.pytest.org/en/7.1.x/how-to/tmp_path.html#tmp-path-handling
        'TMP_BASE_DIR': Path(__file__).resolve().parent.parent,
        'TMP_GIT_REPO_DIR': Path(__file__).resolve().parent.parent / 'tmp' / 'git_tests',
    }

# Custom pytest mark for @pytest.mark.slow (by default will be skipped except if --runslow cli option is given)
# see: https://docs.pytest.org/en/7.1.x/example/simple.html#control-skipping-of-tests-according-to-command-line-option
def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")
def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)