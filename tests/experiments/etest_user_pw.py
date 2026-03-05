"""
Healthy Meals Web Site
Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals

tests/accounts/atest_user_pw.py
- Experimental testing using playwright - Had issues, and found db and rest style tests are sufficient, efficient, and reliable.

"""
import pytest
from distlib.locators import Locator
# from django.test import Client
from django.urls import reverse
from bs4 import BeautifulSoup

from accounts.models import CustomUser
from tests.accounts.factories import CustomUserFactory

from playwright.sync_api import Playwright, sync_playwright, BrowserContext, Page, Browser, expect
# from playwright.async_api import async_playwright, BrowserContext, Page, Browser

import logging
logger = logging.getLogger(__name__)

#############################################################################
# CONSTANTS FOR TESTING

from tests.testing_constants import (
    BAD_PASSWORD,
    INITIAL_PASSWORD,
    RESET_PASSWORD,
    REGUSER_EMAIL,
    REGUSER_FNAME,
    REGUSER_LNAME,
    SUPERUSER_EMAIL,
    SUPERUSER_FNAME,
    SUPERUSER_LNAME,
)


########################################################################################################################
# FIXTURES
########################################################################################################################

# https://testingbot.com/support/web-automate/playwright/pytest
# https://www.opcito.com/blogs/parallel-and-cross-browser-testing-with-playwright
# https://docs.pytest.org/en/stable/how-to/parametrize.html
# https://playwright.dev/python/docs/api/class-locator
# https://playwright.dev/python/docs/api/class-browser
# https://software-testing-tutorials-automation.com/2025/08/playwright-css-selectors.html
# https://pythontest.com/framework/pytest/pytest-parametrize-fixtures/
# https://playwright.dev/docs/pages
# https://python-basics-tutorial.readthedocs.io/en/latest/test/pytest/params.html
# https://playwright.dev/docs/debug#verbose-api-logs


# @pytest.fixture(params=["chromium", "firefox", "webkit"])
# @pytest.fixture()
@pytest.fixture(params=["chromium", "firefox", "webkit"])
def browser_page_pw(playwright: Playwright, request):
    logger.debug(f'\n request.param: {request.param}')
    browser: Browser | None
    match request.param:
        case "chromium":
            browser: Browser = playwright.chromium.launch()
        case "firefox":
            browser: Browser = playwright.firefox.launch()
        case "webkit":
            browser: Browser = playwright.webkit.launch()
        case _:
            raise Exception(f"Unknown browser type: {request.param}")
    logger.debug(f'*** browser_page_pw - {request.param} - browser opened')
    logger.debug(f'*** browser: - {browser} - browser opened')
    context: BrowserContext = browser.new_context()
    page: Page = context.new_page()
    page.set_viewport_size({"width": 1280, "height": 1024})
    # page: Page = browser.new_page()
    page_info = {"page": page, "browser_type": request.param}

    logger.debug('*** browser_page_pw - %(param)s - yield page_info: %(info)s', {'param': request.param, 'info': page_info})
    yield page

    logger.debug(f'*** browser_page_pw - {request.param} - close browser')
    browser.close()


# @pytest.fixture()
# # def chrome_page(playwright: Playwright):
#     browser: Browser = playwright.chromium.launch()
#     # context: BrowserContext = browser.new_context()
#     # page: Page = context.new_page()
#     page: Page = browser.new_page()
#     # page.set_viewport_size({"width": 1280, "height": 1024})
#
#     yield page
#
#     browser.close()

# @pytest.fixture()
# def fire_page(playwright: Playwright):
#     browser: Browser = playwright.webkit.launch()
#     context: BrowserContext = browser.new_context()
#     page: Page = context.new_page()
#     page.set_viewport_size({"width": 1280, "height": 1024})
#
#     yield page
#
#     browser.close()
#
# @pytest.fixture()
# def webkit_page(playwright: Playwright):
#     browser: Browser = playwright.chromium.launch()
#     context: BrowserContext = browser.new_context()
#     page: Page = context.new_page()
#     page.set_viewport_size({"width": 1280, "height": 1024})
#
#     yield page
#
#     browser.close()

# @pytest.mark.parametrize('browser_page_pw', ["chromium", "firefox", "webkit"], indirect=True)
# def test_custom_user_client(playwright: Playwright, bro_name, chrome_page, fire_page, webkit_page):
@pytest.mark.skip(reason="Should Playwright test be supported, if we have Selenium working?")
@pytest.mark.slow
# def test_custom_user_client_js_pw(browser_page_pw):
# def test_custom_user_client_js_pw(live_server, browser_type):
# def test_custom_user_client_js_pw(page: Page, live_server):
def test_custom_user_client_pw(browser_page_pw):
    # This function is repeatedly processed for each parametrized browser
    # print(f'\n request.param: {bro_name}')
    # get the page for this test
    # page: Page | None = None
    # match bro_name:
    #     case "chromium":
    #         page = chrome_page
    #     case "firefox":
    #         page = fire_page
    #     case "webkit":
    #         page = webkit_page
    #     # hard coded so no other possibilities could possibly occur
    #     # case _:
    #     #     raise Exception(f"Unknown browser type: {bro_name}")
    #
    # get home page for user not logged in.
    page = browser_page_pw
    browser_type: str = ""  # browser_page_pw.type
    """Skip this test. Stopping work on playwright js testing:

    .. todo:: fix problems opening localhost:8000 with error: playwright._impl._errors.Error:\
         Page.goto: Could not connect to the server.\
         - navigating to "/", waiting until "load"
    """
    page.goto("/")
    # page.goto(live_server.url + reverse("home"))
    assert page.title() == 'Healthy Meals: Diet Assistant - Home', (
        f'*** {__name__}::test_custom_user_client - {browser_type} - invalid home page title')
    # title: Locator = page.locator('head > title')
    # assert title.inner_text() == 'Healthy Meals: Diet Assistant - Home', f'*** {__name__}::test_custom_user_client {bro_name} - invalid home page title'
    #
    # sign in
    logger.debug(
        f'*** {__name__}::test_custom_user_client - {browser_type} - home main: {page.locator('main main h3').inner_text()}')
    assert page.locator('main main h3').inner_text() == 'Home', (
        f'*** {__name__}::test_custom_user_client - {browser_type} - Home page H3 header is not "Home"')
    log_in_link = js_get_elem(page, '#topSysMenu a:has-text("Log in")', 'Log in')
    logger.debug(f'*** {__name__}::test_custom_user_client - {browser_type} - click login link')
    '''.. todo:: resolve issue so `force=true` is not needed for click on login link.'''
    # log_in_link.click(force=True)
    log_in_link.click()
    logger.debug(f'*** {__name__}::test_custom_user_client - {browser_type} - clicked login link')
    #
    # fill in and submit log in form
    logger.debug(
        f'*** {__name__}::test_custom_user_client - {browser_type} - main main: {page.locator('main main').inner_text()}')
    # assert page.locator('main main form label[for="id_login"]').inner_text() == 'Email', (
    #     f'*** {__name__}::test_custom_user_client - {browser_type} - login  form is missing label for Email input field')
    '''.. todo:: find out why form fields are getting `Timeout 30000ms exceeded - waiting for locator("#id_login")`.'''
    page.locator('#id_login').fill(REGUSER_EMAIL)
    page.locator('#id_password').fill(INITIAL_PASSWORD)
    page.locator('#topSysMenu button:has-text("Log in")').click(force=True)
    #
    # confirm we are signed in

    # ########
    # # at end of test, close browser?
    # browser.close()


#############################################
# Check About page displays

#############################################
# Check Logged in - change password process works correctly

#############################################
# Check log out process works correctly

#############################################
# Check password change process works correctly

#############################################
# Check password reset process works correctly

#############################################
# Check signup process works correctly


########################################################################################################################
# REGULAR / MODULE LEVEL TEST SUPPORT FUNCTIONS
########################################################################################################################

def js_get_elem(page: Page, css: str, text: str):
    """fixture for playwright element locator debugging and common assertions."""
    elem = page.locator(css)
    assert elem.count() == 1, '*** js_locate_one_elem - more than one element returned'
    assert elem.is_visible(), '*** js_locate_one_elem - element is not visible'
    assert elem.inner_text() == text, f'*** js_locate_one_elem - element text is not {text}'
    return elem
