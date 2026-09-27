import logging
logger = logging.getLogger(__name__)
'''
Healthy Meals Web Site
Copyright (C) 2025 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals - tests/nox/test_local_nox.py
'''
import pytest
from subprocess import run

@pytest.mark.skip(reason="Is this untestable? Do dev tools need to be tested? Delete this?")
def test_local_nox_scripts():
    '''Ensure nox scripts are working on the local server

    Steps:
    - 
    - use curl to request a web page, and confirm it is the correct response
    - run the local testing command
    - run the local sphinx docs command
    - other local commands?
    '''
    logger.debug('***    Starting tests/nox/test_local_nox.py::test_local_nox_scripts')

    # show starting message
    logger.debug('*** 1 - Start by running local server in the background (localUp)')
    ret = run(["nox", "-s", "localUp"])
    assert ret.returncode == 0, 'Error running nox -s localUp'
