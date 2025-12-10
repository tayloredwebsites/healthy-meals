import os

import pytest
import time

from allauth.account.auth_backends import AuthenticationBackend
from django.core import mail

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from tests.accounts.conftest import validate_user_email  # get_or_create_custom_user
from tests.accounts.factories import CustomUserFactory
from tests.conftest import click_and_wait, get_and_wait, screenshot, find_and_refill

# from django.contrib.auth import get_user_model
from unittest.mock import patch
from accounts.models import EmailAddress
# from accounts.models import CustomEmailAddress
from accounts.models import CustomUser

# from allauth.account.auth_backends import authenticate


import logging

########################################################################################################################
# CONSTANTS FOR TESTING

from tests.testing_constants import (
    INITIAL_USER_EMAIL,
    INITIAL_USER_PASSWORD,
    SIMPLE_PASSWORD,
    INITIAL_USER_FNAME,
    INITIAL_USER_LNAME,
    INITIAL_USERNAME,
)

"""
    .. todo:: add a version of testing to nox with the --runslow option so that selenium tests marked as slow will run.
"""


#############################################################################
@pytest.mark.slow
def test_signup_e2e(selenium, live_server):
    """Confirm CustomUser Allauth signup pages work using selenium

    Notes::
        - For Selenium to use Firefox, Chromium, or both, see tests/conftest.py:selenium() fixture, and select appropriate params in the fixture.
        - see: `Allauth configuration docs <django-allauth.readthedocs.io/en/latest/account/configuration.html>`_
    """

    logger = logging.getLogger(__name__)

    # selenium.maximize_window()
    # selenium.set_window_size(800, 600)
    logger.debug(f'live_server.url is {live_server.url}')

    # --------------------------------------------------------------------
    logger.debug('*** Confirm we are on the home page')
    assert selenium.title == 'Healthy Meals: Diet Assistant - Home'

    # --------------------------------------------------------------------
    logger.debug('*** Go To sign up form (so we have someone to log in as)')
    click_and_wait(driver=selenium, click_css='#topSysMenu a#signup_link', match_css='form#signup_form')

    # --------------------------------------------------------------------
    logger.debug('*** Sign up with simple password to fail')
    find_and_refill(selenium, find_css='input#id_email', fill=VALID_EMAIL)
    find_and_refill(selenium, find_css='input#id_password1', fill=SIMPLE_PASSWORD)
    find_and_refill(selenium, find_css='input#id_password2', fill=SIMPLE_PASSWORD)
    # time.sleep(5)
    error_element = click_and_wait(driver=selenium, click_css='form#signup_form button',
                                   match_css='div#div_id_password1 .invalid-feedback')
    print('*** Sign up with simple password to fail')
    assert selenium.title == 'Healthy Meals: Diet Assistant - Sign up'
    assert error_element.text == (
        'This password is too common.'), 'allows a password of "password"'

    # --------------------------------------------------------------------
    logger.debug('Sign up with empty second password to indicate mismatched passwords')
    find_and_refill(selenium, find_css='input#id_email', fill=VALID_EMAIL)
    find_and_refill(selenium, find_css='input#id_password1', fill=VALID_PASSWORD)
    find_and_refill(selenium, find_css='input#id_password2', fill='')
    # time.sleep(5)
    error_element = click_and_wait(driver=selenium, click_css='form#signup_form button',
                                   match_css='div#div_id_password1 .invalid-feedback')
    print('*** click_and_wait for bad password failure')
    assert selenium.title == 'Healthy Meals: Diet Assistant - Sign up'
    assert error_element.text == (
        'This password is too common.'), 'the errors on this are misleading.'

    """.. todo:: blank second password should indicate mismatched or blank second password"""

    # --------------------------------------------------------------------
    logger.debug('Sign up with mismatched password to fail')
    find_and_refill(selenium, find_css='input#id_email', fill=VALID_EMAIL)
    find_and_refill(selenium, find_css='input#id_password1', fill=VALID_PASSWORD)
    find_and_refill(selenium, find_css='input#id_password2', fill=NEW_PASSWORD)
    # time.sleep(5)
    error_element = click_and_wait(driver=selenium, click_css='form#signup_form button',
                                   match_css='div#div_id_password2 .invalid-feedback')
    print('*** click_and_wait for bad password failure')
    assert selenium.title == 'Healthy Meals: Diet Assistant - Sign up'
    assert error_element.text == (
        'You must type the same password each time.'), 'allows mismatch passwords on signup'

    """.. todo:: mismatched passwords on signup does not give an err"""

    # --------------------------------------------------------------------
    logger.debug('Sign up Successfully and get the email, and the "Verify Email Address Page"')

    logger.debug('get email outbox length')
    email_1_ref = len(mail.outbox)  # length of email messages list, should start out at zero

    logger.debug('fill in the form')
    find_and_refill(selenium, find_css='input#id_email', fill=VALID_EMAIL)
    find_and_refill(selenium, find_css='input#id_password1', fill=VALID_PASSWORD)
    find_and_refill(selenium, find_css='input#id_password2', fill=VALID_PASSWORD)
    click_and_wait(driver=selenium, click_css='form#signup_form button', match_css='main main p')

    print('*** Make sure that one email message got sent on user account signup successful creation')

    time.sleep(0.3)  # wait for mail outbox to get populated from message

    logger.debug('verify we got the "confirm email address" email')
    assert len(mail.outbox) == email_1_ref + 1
    assert mail.outbox[email_1_ref].to == [VALID_EMAIL]
    assert mail.outbox[email_1_ref].from_email == 'root@localhost'
    assert 'Please Confirm Your Email Address' in mail.outbox[email_1_ref].subject
    assert 'To confirm this is correct,' in mail.outbox[email_1_ref].body, 'this is not the frst confirmation message'
    # print(f'body of first message: {mail.outbox[email_1_ref].body}')

    logger.debug('verify the web page is correct.')
    element = selenium.find_element(By.CSS_SELECTOR, 'main main p')
    assert 'We have sent an email to you for verification.' in element.text

    # --------------------------------------------------------------------
    logger.debug('Go To sign up form and see what happens if we try to sign up without verifying our email')
    click_and_wait(driver=selenium, click_css='#topSysMenu a#signup_link', match_css='form#signup_form')

    # get email outbox length
    email_2_ref = len(mail.outbox)
    find_and_refill(selenium, find_css='input#id_email', fill=VALID_EMAIL)
    find_and_refill(selenium, find_css='input#id_password1', fill=VALID_PASSWORD)
    find_and_refill(selenium, find_css='input#id_password2', fill=VALID_PASSWORD)
    click_and_wait(driver=selenium, click_css='form#signup_form button', match_css='html')
    logger.debug('*** Make sure that one email message got sent on user account signup successful creation')
    time.sleep(0.1)  # wait for mail outbox to get populated from message
    assert len(mail.outbox) == email_2_ref + 1
    assert 'However, an account using that email address already exists.' in mail.outbox[email_2_ref].body

    logger.debug(f'*** body of the second message: {mail.outbox[email_2_ref].body}')

    """.. todo:: test_custom_user_e2e research to see if email accounts are recycled if not verified"""

    # --------------------------------------------------------------------
    logger.debug('simulate a user properly verifying their email address')
    # time.sleep(10)
    found_user, email_obj = validate_user_email(VALID_EMAIL)

    logger.debug('*** go to home page to log in, also confirming we are still logged out.')

    # --------------------------------------------------------------------
    logger.debug('start at home, and log in with valid user')
    get_and_wait(driver=selenium, live_server=live_server, url='/')
    assert selenium.title == 'Healthy Meals: Diet Assistant - Home'

    login_link: WebElement = selenium.find_element(By.CSS_SELECTOR, '#topSysMenu a#login_link')
    assert login_link.text == 'Log in'

    # --------------------------------------------------------------------
    logger.debug('*** Go To login form')
    click_and_wait(driver=selenium, click_css='#topSysMenu a#login_link', match_css='html')
    # time.sleep(5)

    # --------------------------------------------------------------------
    logger.debug('*** login with empty password should fail')
    find_and_refill(selenium, find_css='input#id_login', fill=VALID_EMAIL)
    find_and_refill(selenium, find_css='input#id_password', fill=INVALID_PASSWORD)
    # time.sleep(5)
    error_field = click_and_wait(driver=selenium, click_css='form#login_form button',
                                 match_css='form#login_form .alert')
    # time.sleep(5)
    assert 'are not correct.' in error_field.text, (
        'did not get invalid email or password message')

    print('*** Go To login form')
    chg_pwd_link = click_and_wait(driver=selenium, click_css='#topSysMenu a#login_link', match_css='html')
    print('*** login')
    find_and_refill(selenium, find_css='input#id_login', fill=VALID_EMAIL)
    find_and_refill(selenium, find_css='input#id_password', fill=VALID_PASSWORD)
    # time.sleep(5)
    chg_pwd_link = click_and_wait(driver=selenium, click_css='form#login_form button', match_css='html')
    # time.sleep(5)

    """.. todo:: solve problem logging in using the test system.
        .. code-block:: python

            err_str = selenium.find_element(By.CSS_SELECTOR, 'form#login_form div.alert li').text
            assert 'are not correct' not in err_str, (
                'did not login in with correct email and password')
            
        Notes:
        
            - try getting response, check for errors and status
            - could it be looking for username?
    """

    # screenshot(driver=selenium)


########################################################################################################################
@pytest.mark.slow
def test_login_e2e(selenium, live_server):
    """Confirm CustomUser allauth change password pages work using selenium

    Notes::
        - For Selenium to use Firefox, Chromium, or both, see tests/conftest.py:selenium() and select appropriate params.
    """
    # logger = logging.getLogger(__name__)
    # logger.debug(f'*** nox -s dockerUpBg - started')

    """Confirm CustomUser Allauth signup pages work using selenium"""
    # selenium.maximize_window()
    # selenium.set_window_size(800, 600)
    print(f'live_server.url is {live_server.url}')
    # selenium.get(live_server.url) # to view django live server
    assert selenium.title == 'Healthy Meals: Diet Assistant - Home'

    # -------------------------------------------------------------------------------------------------------------------
    # create and validate user
    # new_user_info, new_user_errors, new_user = get_or_create_custom_user(
    #     email=VALID_EMAIL,
    #     username=VALID_EMAIL,
    #     password=VALID_PASSWORD,
    #     # is_active=True,
    # )
    # print(f'new user: {new_user:detail}')
    # found_user, email_obj = validate_user_email(VALID_EMAIL)
    user = CustomUserFactory.create(
        email=VALID_EMAIL,
        username=VALID_EMAIL,
        password=VALID_PASSWORD,
    )
    print(f'saved user: {user:detail}')
    # assert CustomUser.objects.count() == 1, 'the signed_in_user is not the only user at the start of test'
    # email_rec = CustomEmailAddress.objects.create(user=user, email=VALID_EMAIL, verified=True, primary=True)
    email_rec = EmailAddress.objects.create(user=user, email=VALID_EMAIL, verified=True, primary=True)
    print(f'email_rec: {email_rec:detail}')
    user.set_password(VALID_PASSWORD)

    found_user, email_obj = validate_user_email(VALID_EMAIL)
    # client.force_login(user)

    # -------------------------------------------------------------------------------------------------------------------
    # start at home, and log in with valid user
    # get home page for logged in user

    print('*** Screenshot started')
    screenshot(driver=selenium)

    print('*** Screenshot finished')
    get_and_wait(driver=selenium, live_server=live_server, url='/')
    assert selenium.title == 'Healthy Meals: Diet Assistant - Home'
    # time.sleep(5)
    chg_pwd_link = click_and_wait(driver=selenium, click_css='#topSysMenu a#login_link', match_css='html')
    find_and_refill(selenium, find_css='input#id_login', fill=VALID_EMAIL)
    find_and_refill(selenium, find_css='input#id_password', fill=INVALID_PASSWORD)
    # time.sleep(5)
    chg_pwd_link = click_and_wait(driver=selenium, click_css='form#login_form button', match_css='html')
    # time.sleep(5)

    screenshot(driver=selenium)

    err_str = selenium.find_element(By.CSS_SELECTOR, 'form#login_form div.alert li').text
    assert 'are not correct' in err_str

    # screenshot(driver=selenium)


########################################################################################################################
@pytest.mark.slow
def test_change_pwd_e2e(selenium, live_server):
    """Confirm CustomUser allauth change password pages work using selenium"""

    logger = logging.getLogger(__name__)

    # -------------------------------------------------------------------------------------------------------------------
    # create and validate user
    # new_user_info, new_user_errors, new_user = get_or_create_custom_user(
    #     email=VALID_EMAIL,
    #     username=VALID_EMAIL,
    #     password=VALID_PASSWORD,
    #     # is_active=True,
    # )
    # print(f'new user: {new_user:detail}')
    # found_user, email_obj = validate_user_email(VALID_EMAIL)
    user = CustomUserFactory.create(
        email=VALID_EMAIL,
        username=VALID_EMAIL,
        password=VALID_PASSWORD,
    )
    print(f'saved user: {user:detail}')

    email_rec = EmailAddress.objects.create(user=user, email=VALID_EMAIL, verified=True, primary=True)
    print(f'email_rec: {email_rec:detail}')
    # user.set_password(VALID_PASSWORD)

    found_user, email_obj = validate_user_email(VALID_EMAIL)

    # --------------------------------------------------------------------
    logger.debug('*** Go To login form')
    click_and_wait(driver=selenium, click_css='#topSysMenu a#login_link', match_css='html')
    # time.sleep(5)

    # --------------------------------------------------------------------
    print('*** login with invalid password should fail')
    find_and_refill(selenium, find_css='input#id_login', fill=VALID_EMAIL)
    find_and_refill(selenium, find_css='input#id_password', fill=INVALID_PASSWORD)
    # time.sleep(5)
    screenshot(driver=selenium)
    error_field = click_and_wait(driver=selenium, click_css='form#login_form button',
                                 match_css='form#login_form .alert')
    # time.sleep(5)
    assert 'password you specified are not correct.' in error_field.text, (
        'did not get invalid email or password message')
