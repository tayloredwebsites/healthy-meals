# tests (root) conftest.py

"""root conftest.py file for configuration of all tests

    Notes::

        - have the the ability to mark tests with @pytest.mark.slow
        - selenium() fixture added for javascript testing using selenium live server
            - webkit/safari is commented out because of these issues:
                - https://developer.apple.com/documentation/webkit/testing-with-webdriver-in-safari
                - it does not appear to support headless testing, which is not good for CI
                - document safari webdriver enable command (safaridriver --enable) needed for Mac security
                - needs development of code for non-mac testing of webkit/safari browsers
            - references
                - use live_server in pytest fixture: https://stackoverflow.com/questions/31937472/django-pytest-selenium
            - Chrome Implementation (initial):
                - Chrome version handling: https://wikomtech.com/blog/chrome-for-testing-browser-use-case-with-selenium-in-python/
                - Chrome for Testing (no automatic version changes): https://developer.chrome.com/blog/chrome-for-testing/
                - npx puppeteer to download and launch chrome versions: https://paultreanor.com/browser-testing
                - using ChromeOptions: https://www.browserstack.com/guide/selenium-chrome-options
                - using ChromeOptions: https://developer.chrome.com/docs/chromedriver/capabilities
                - chromedriver path: https://stackoverflow.com/questions/12698843/how-do-i-pass-options-to-the-selenium-chrome-driver-using-python
                - wait for page to load: https://www.selenium.dev/documentation/webdriver/waits/
            - Firefox
                - https://stackoverflow.com/questions/42204897/how-to-set-up-a-selenium-python-environment-for-firefox#answer-42230592
                - download geckodriver: https://github.com/mozilla/geckodriver/releases
                - https://www.selenium.dev/documentation/webdriver/troubleshooting/errors/driver_location/


    .. todo::
        - selenium_web followup:
            - add firefox version selection (see chrome configs file)
            - add selenium log outputs to console
            - add webkit/safari testing if it can be run as headless
            - document or simplify removing headless option for debugging tests
            - document selenium setup and config json file loading
        - review need for get_superuser_info(), get_logged_in_superuser(), and get_case_superuser1() fixtures
        - clean up unneeded commented out code.

"""
import inspect
import re
from datetime import datetime, timezone
from pprint import pprint
from typing import Callable

import pytest
import pytest_html
from bs4 import BeautifulSoup
from django.test import Client
from pytest_django.live_server_helper import LiveServer
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
import time
import os

from django.conf import settings

# from decouple import config

import logging

logger = logging.getLogger(__name__)

# from accounts.models import CustomUser
# from tests.accounts.factories import CustomUserFactory, SuperUserFactory
# from django.db import connection
# import inspect

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
# from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import subprocess

import json

# from accounts.requirements import CustomUserRequirements

'''Testing Philosophy and Tool Choices:
    - 'Client Based' testing is what I will call the Healthy Meals preferred automate testing set of tools.
        - See 'tests/accounts/custom_user_client.py' as the initial example developed.
        - Uses pytest because it can do all of the testing required, and because I prefer reading and writing pytest tests.
        - Uses @pytest.mark.django_db' so we can check for updates to the models in the database through out the tests.
        - Uses client (from django_db fixture) to do 'GET' and 'POST' calls to the server
        - Uses BeautifulSoup to check the web pages generated from 'GET' and 'POST' calls
        - all links should be confirmed (at least once per page), by:
            - 1. getting the url
            - 2. get the page at the url using client.get()
            - 3. confirming it goes to the expected page using BeautifulSoup
        - all forms should be confirmed (at least once per page), by:
            - 1. get all of the fields in the form (including hidden ones)
            - 2. do multiple posts as appropriate, so as to:
                - 2a. cover all combinations of valid and invalid data.
                - 2b. analyze for all edge cases, and test for them.
        - Organize tests so they are grouped in the following ways:
            - By user action flows with one longer test per each user action flow, thereby:
                - we minimize test preparation and tear down.
                - the tests correspond directly to user actions.
                - this makes resolving bugs in user flows easier to find in tests.
                - makes the tests easier to read (assuming the reader is familiar with the site).
                - this makes the tests easier to ensure that we are covering edge cases in the user flow.
            - By covering edge cases and error handling flows organized in a logical way.
            - Focus of tests are thereby on how the application works, which is generally sufficient:
                - unit testing is less important here, because we are not writing a library.
                - by providing close to 100% coverage of all files that generate pages:
                    - we tend to provide the benefits of unit tests for all code.
        - This choice of tools are very efficient, and provide for fast and efficient automated test runs.
        - Special considerations:
            - It is still important that when looking a code coverage, that edge case analysis is done.
            - For javascript code testing, it will be important to provide a live browser.
                - see playwright and selenium Testing Tools notes below.
    - The Admin interface will be valuable to minimize crud programming:
        - it will be important there to be full coverage of the admin interface (see todo below).
        - see '/tests/accounts/test_custom_user_admin.py'
    - Testing Tools tried and are currently being skipped (see examples in /tests/accounts/ directory):
        - TestCase:
            - did not want to have two separate testing systems, and saw pytest could integrate in TestCase tests
            - had issues with the integration with pytest. see: ????
            - see tests/accounts/custom_user_cases.py
        - Playwright:
            - These tests were skipped, as there were issues running them see: ????
        - Selenium:
            - These tests worked well, but were skipped because:
                - 'Client Based' testing will be best and sufficient until javascript testing will be needed.
            - When javascript tests are needed, they should only supplement the 'Client Based' tests
            - see '/tests/accounts/test_custom_user_e2e.py'
            - see also the selenium fixture here in '/tests/conftest.py'
            - Minor issues were:
                - as browsers are upgraded, the drivers will need to be downloaded to the developers and CI system
                - live browsers will always be slower tests
                - the firefox driver was the only one I figured out how to output the selenium debugging statements.
                - This was only tested on a Mac
                - the webkit / safari was unable to be run headless.
    - Note: this is an example of how to document close to the code, for better maintenance.
    .. todo:: Use and have full coverage of the admin interface to minimize crud programming:
'''

########################################################################################################################
# CONSTANTS FOR TESTING

CHROME_VERSION = '143.0.7499.169'
FIREFOX_VERSION = '0_36_0'
FIREFOX_DRIVER_PATH = '/Users/dave/works/local_src/firefox_0_36_0/geckodriver'
SELENIUM_TMP_DIR = '/tmp/selenium'


# FIREFOX_SELENIUM_PROFILE = r'/Users/dave/Library/Application Support/Firefox/Profiles/5ldfqpsx.Selenium/'

########################################################################################################################
#  utility methods for pytest flags


# ----------------------------------------------------------------------------------------------------------------------
# pytest command line options (pytest_addoption)
# all options must be declared together

def pytest_addoption(parser):
    """Custom pytest command line options

    Notes::

        - --runslow option:
            - add the ability to mark tests with @pytest.mark.slow:
            - tests with @pytest.mark.slow will be skipped unless --runslow cli option is given
            - see: https://docs.pytest.org/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option
            - pytest_addoption() works with pytest_configure(), and pytest_collection_modifyitems() methods
  """

    parser.addoption(
        "--runslow",
        action="store_true",
        default=False,
        help="only run slow tests when --runslow option is given",
    )


# ----------------------------------------------------------------------------------------------------------------------
# pytest marker configurations

def pytest_configure(config):
    """set the test markers"""

    # --runslow configuration
    config.addinivalue_line("markers", "slow: mark test as slow to run")


# ----------------------------------------------------------------------------------------------------------------------
# skip options by keyword for runslow and requirements

def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return

    """code to skip slow tests if --runslow option is given"""
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


########################################################################################################################
# PYTEST FIXTURES

# ----------------------------------------------------------------------------------------------------------------------
# selenium web driver

@pytest.fixture(params=["firefox"])  # ["chromium", "firefox"])
def selenium(live_server, request):
    """selenium webdriver pytest fixture for end to end testing of javascript code, clicks and other actions

        Examples::

            def test_something_e2e(selenium, live_server):
                get_and_wait(selenium, live_server, '/')
                # or # get_and_wait(driver=selenium, live_server=live_server, url='/')
                assert selenium.title == 'Healthy Meals: Diet Assistant - Home'
    """
    logger.debug('\n browser selection from request.param: %s', request.param)
    # browser: Browser | None
    selenium: WebDriver | None = None
    match request.param:
        case "chromium":
            with open('/Users/dave/works/local_src/chrome_config.json') as f:
                all_configs_txt = f.read().replace('\n', '')
                logger.debug('*** all_configs_txt: %s', all_configs_txt)
                all_configs_dict = json.loads(all_configs_txt)
                ver_config = all_configs_dict[CHROME_VERSION]
                # logger.debug(f'*** ver_config: {ver_config}')
                # logger.debug(f'*** ver_config[chrome_driver]: {ver_config["chrome_driver"]}')
                driver_path = ver_config['chrome_driver']
                service = ChromeService(executable_path=driver_path)
                # service = webdriver.ChromeService(service_args=['--log-level=DEBUG'], log_output=subprocess.STDOUT)
                options = webdriver.ChromeOptions()
                options.add_argument(f'executable_path={driver_path}')
                """
                .. todo:: get selenium chrome driver display of webdriver logging statements working properly
                    - see: www.selenium.dev/documentation/webdriver/browsers/chrome/

                .. code-block:: python

                    # options.set_capability('goog:loggingPrefs', {'browser': 'SEVERE'})
                    # options.set_capability('goog:loggingPrefs', {'browser': 'WARNING'})
                    # options.set_capability('goog:loggingPrefs', {'browser': 'INFO'})
                    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
                    # options.add_argument('--enable-logging')
                    # options.add_argument('--v=1')

                    # # attempt to output chrome logs at end (after yield))
                    # if request.param == "chromium":
                    #     # get log to output to console at end for Chrome
                    #     logs = selenium.get_log('browser')
                    #     for entry in logs:
                    #         logger.debug(f'SEL_LOG: {entry["message"]}')

                """

                """To control display of web pages to browser, comment or uncomment out the --headless option below"""
                options.add_argument("--headless")
                selenium: WebDriver = webdriver.Chrome(options=options)

        case "firefox":
            # selenium: WebDriver | None = None
            options = webdriver.FirefoxOptions()
            options.add_argument(f'executable_path="{FIREFOX_DRIVER_PATH}"')

            """To control the display of the logging level from the selenium webdriver for Firefox :
                - see: www.selenium.dev/documentation/webdriver/browsers/firefox/
                - uncomment the appropriate service line below

            .. todo:: be able to set selenium firefox driver logger to not always be debug level
            """
            #
            service = webdriver.FirefoxService(log_output=subprocess.STDOUT, service_args=['--log', 'fatal'])
            # service = webdriver.FirefoxService(log_output=subprocess.STDOUT, service_args=['--log', 'error'])
            # service = webdriver.FirefoxService(log_output=subprocess.STDOUT, service_args=['--log', 'info'])
            # service = webdriver.FirefoxService(log_output=subprocess.STDOUT, service_args=['--log', 'debug'])

            """To control display of web pages to browser, comment or uncomment out the --headless option below"""
            options.add_argument("--headless")

            selenium: WebDriver = webdriver.Firefox(options=options, service=service)
        case _:
            raise Exception(f"Unknown browser type: {request.param}")

    """
        .. todo::  research if webkit can be run as headless in selenium webdriver.

        .. code-block:: python

            case "webkit": # (safari) driver is built into Macs
                options = webdriver.SafariOptions()
                # options.add_argument("--headless")
                driver = webdriver.Safari()
    """

    get_and_wait(selenium, live_server, '/')
    logger.debug('*** yield Selenium WebDriver')
    yield selenium

    logger.debug('*** close the Selenium WebDriver')
    selenium.quit()
    """.. todo:: solve errors when quitting selenium (on mac?):

            - console.error: "Failed to fetch https://spocs.getpocket.com/user:" "NetworkError when attempting to fetch resource."
            - console.error: (new TypeError("NetworkError when attempting to fetch resource.", ""))
            - console.error: (new Error("HTTP was configured for https://ads.mozilla.org/v1/delete_user but we couldn't fetch a valid config", "moz-src:///browser/modules/ContextId.sys.mjs", 234))
            - console.warn: TopSitesFeed: Failed to fetch data from MARS server: NetworkError when attempting to fetch resource.
            - JavaScript error: resource://gre/modules/ObliviousHTTP.sys.mjs, line 117: NS_ERROR_XPC_CANT_CONVERT_PRIMITIVE_TO_ARRAY: Cannot convert primitive JavaScript value into an array arg 2 [nsIObliviousHttpService.newChannel]

        .. code-block:: python

            # attempts to solve errors when quitting selenium:
            options.set_preference("extensions.pocket.enabled", False)
            options.set_preference("marionette", False)
            profile = webdriver.FirefoxProfile(FIREFOX_SELENIUM_PROFILE)  # Creates a new profile using profile created through firefox
            profile.set_preference("browser.newtabpage.activity-stream.feeds.topsites", False)
            options.profile = profile
    """


########################################################################################################################
#  Utility functions for Selenium testing
########################################################################################################################

def click_and_wait(driver: WebDriver, click_css: str, match_css: str):
    """Selenium testing: click on click_css element, and wait until match_css element is present"""
    logger.debug('click_and_wait click_css: %s', click_css)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, click_css)))
    element_to_click: WebElement = driver.find_element(By.CSS_SELECTOR, click_css)
    element_to_click.click()
    logger.debug('click_and_wait match_css: %s', match_css)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, match_css)))
    element_to_wait_for: WebElement = driver.find_element(By.CSS_SELECTOR, match_css)
    return element_to_wait_for


def get_and_wait(driver: WebDriver, live_server: LiveServer, url: str):
    """Selenium testing: get url, and wait until match_css element is present"""
    logger.debug('get_and_wait url: %(base_url)s%(path)s', {'base_url': live_server.url, 'path': url})
    driver.get(live_server.url + url)  # to view django live server
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'html')))


def screenshot(driver: WebDriver, filename_note: str = '', save_png: bool = False):
    """Selenium testing: generate a html, and optionally a png screenshot in the tmp/selenium directory

    Args:
        driver (class): the Selenium WebDriver instance
        filename_note (str): string to include in the filename
            - will be truncated to 30 characters to keep filename length sane
            - only alphanumerics, underscore, and decimal point characters are allowed, rest will be removed
    """
    logger.debug('screenshot started')
    logger.debug('screenshot filename_note: %s', filename_note)
    os.makedirs('tmp/selenium', exist_ok=True)
    logger.debug('screenshot 2')
    timestamp = datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f')
    logger.debug('screenshot 3')
    note = re.sub(r'[^a-zA-Z0-9_\.]', '', filename_note)[:30]
    logger.debug('screenshot 4')
    if save_png:
        # defaulted to false, because of large messages to console.
        # driver.save_full_page_screenshot(f'tmp/selenium/screen_{timestamp}_{note}_shot.png')
        driver.save_screenshot(f'tmp/selenium/screen_{timestamp}_{note}_shot.png')
    logger.debug('screenshot 5')
    page_html = driver.page_source
    logger.debug('screenshot 6')
    with open(f'tmp/selenium/screen_{timestamp}_{note}.html', 'w') as f:
        f.write(page_html)
    logger.debug('screenshot finished')


def find_and_refill(driver: WebDriver, find_css: str, fill: str):
    """Selenium testing: find a field by css, clear it, and fill it"""
    field = driver.find_element(By.CSS_SELECTOR, find_css)
    field.clear()
    field.send_keys(fill)


########################################################################################################################
#  Utility functions for Client REST Testing (Get, Post, Parse, Find Testing)
########################################################################################################################

def soup_screenshot(resp_content_html: BeautifulSoup, filename_note: str = ''):
    """testing with beautiful soup: save html screenshot in the tmp/soup directory

    Args:
        resp_content_html (BeautifulSoup): the html parsed response from Beautiful Soup
        filename_note (str): string to include in the filename
            - will be truncated to 30 characters to keep filename length sane
            - only alphanumerics, underscore, and decimal point characters are allowed, rest will be removed

    Example:

        .. code-block:: python

            soup = BeautifulSoup(resp.content, 'html.parser')
            soup_screenshot(soup)

    """
    logger.debug('soup screenshot started')
    # logger.debug(f'soup creenshot filename_note: {filename_note}')
    os.makedirs('tmp/soup', exist_ok=True)
    # logger.debug(f'screenshot 2')
    timestamp = datetime.now().strftime('%Y_%m_%d_%H:%M:%S.%f')
    # logger.debug(f'screenshot 3')
    note = re.sub(r'[^a-zA-Z0-9_\.]', '', filename_note)[:30]
    # logger.debug(f'screenshot 4')
    with open(f'tmp/soup/screen_{timestamp}_{note}.html', 'w') as f:
        f.write(resp_content_html.prettify())
    logger.info(f'%%%% soup_screenshot output to tmp/soup/{timestamp}_{note}.html')


def client_rest_call(rest_method: str, url: str, data: dict, element_validations: dict):
    """
        .. todo:: consider doing a refactor of testing client gets and posts:

        - create a test utility function to refactor get and post call standard code to:

            - does get or post, ... to the url, with data as appropriate
            - if no valid_forwarded_url, confirm 200
            - if was passed a valid_forwarded_url_re, confirm 302, validate forward, then call with follow=true, confirm 200
            - return a Beautiful soup parsing of the page.
            - validate page elements in dictionary, with element, and expected value

        - design of the method:
            - one parameter to indicate if its a get, post, patch, or delete method
            - one parameter for the url
            - 'data' parameter for the data, if needed

    """
