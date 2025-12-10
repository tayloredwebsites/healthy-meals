import re
from http.client import HTTPResponse

import pytest
from unittest.mock import patch

import requests
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client
from django.urls import reverse
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt
from requests import Response

from accounts.models import CustomUser
from common.utils.user_utils import get_or_create_superuser
from tests.accounts.conftest import get_url_from_email_body, is_user_email_validated
# from tests.accounts.conftest import truncate_custom_users
from tests.accounts.factories import CustomUserFactory
from common.utils import user_utils

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

''' .. todo:: put in password complexity safeguard tests.'''


#############################################################################
@pytest.mark.django_db
def test_custom_user_signup_client():  # get_init_user):
    logger = logging.getLogger(__name__)
    logger.debug(f'*** {__name__}::test_custom_user_signup_client - Starting')
    client = Client()

    assert CustomUser.objects.count() == 0, (
        'There should be no CustomUser instances')

    # --------------------------------------------------------------------
    logger.debug('*** get Home page, and validate home page header links for logged out user.')
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting home page')
    assert not resp.wsgi_request.user.is_authenticated, (
        'User should not be authenticated')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'soup: {soup}')
    assert soup.h1.get_text() == 'Healthy Meals: Diet Assistant', (
        'Error, should be at the Healthy Meals site')
    assert soup.h2.get_text() == 'Home', (
        'Error, should be at Healthy Meals Home Page')
    elem_menu = soup.find(id='topSysMenu')
    assert elem_menu.find(id='tsm_friend').get_text() == 'Friend', (
        'Error, home page does not show friend, we should not be logged in')
    assert elem_menu.find('a', href='/accounts/logout/') is None, (
        'Error, should not be logged in, and should not show Logout link')
    assert elem_menu.find('a', href='/accounts/password/change/') is None, (
        'Should not be logged in, and should not show Password Change link')
    assert len(elem_menu.find('a', href='/accounts/login/')) == 1, (
        'Error, should not be logged in and should not show Login link')
    assert len(elem_menu.find('a', href='/accounts/signup/')) == 1, (
        'Error, should not be logged in and should not show Signup link')
    assert len(soup.find('a', href='/accounts/password/reset/')) == 1, (
        'Error, should show Password Reset link')

    # --------------------------------------------------------------------
    logger.debug(f'*** get signup page for form')
    resp = client.get(reverse('account_signup'))
    assert resp.status_code == 200, (
        'Error, get signup page should return 200')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.find('h2').get_text() == 'Sign up', (
        'Error, we are not on the Sign up page')
    form_elem = soup.find('form')
    button_elem = form_elem.find('button')
    assert 'Sign up' in button_elem.get_text(), 'Error, unable to find Sign up button on what should be the signup page'
    # csrf_elem = form_elem.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    # assert csrf_elem is not None, (
    #     'Error, cannot find csrf token')
    # assert csrf_elem['name'] == 'csrfmiddlewaretoken', (
    #     'Error getting csrf token')

    # --------------------------------------------------------------------
    logger.debug('post account signup for user to fail with mismatched password')
    resp = client.post(reverse('account_signup'), {
        # csrf_elem['name']: csrf_elem['value'],
        'email': INITIAL_USER_EMAIL,
        'password1': INITIAL_USER_PASSWORD,
        'password2': SIMPLE_PASSWORD,
    })
    assert resp.status_code != 302, (
        'Error, should not redirect, but remain on account signup after error')
    """.. todo:: account signup should return 401 when invalid signup
        - see `HTML Error 401 <www.rfc-editor.org/rfc/rfc7235#section-3.1)>`_"""
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.find('h2').get_text() == 'Sign up', (
        'Error, we are not on the Sign up page')
    assert soup.find(id='error_1_id_password2').get_text() == 'You must type the same password each time.', (
        'Error, did not get password error')

    # --------------------------------------------------------------------
    logger.debug('post account signup for user to fail with password too simple')
    resp = client.post(reverse('account_signup'), {
        # csrf_elem['name']: csrf_elem['value'],
        'email': INITIAL_USER_EMAIL,
        'password1': SIMPLE_PASSWORD,
        'password2': SIMPLE_PASSWORD,
    })
    assert resp.status_code != 302, (
        'Error, should not redirect, but remain on account signup after error')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.find('h2').get_text() == 'Sign up', (
        'Error, we are not on the Sign up page')
    assert soup.find(id='error_1_id_password1').get_text() == 'This password is too common.', (
        'Error, did not get password too common error')

    # --------------------------------------------------------------------
    logger.debug('post account signup for user success')
    # get current length of email outbox, which is also a zero relative pointer
    email_pointer = len(mail.outbox)
    assert email_pointer == 0, (
        'Email outbox length does not start at 0, database is not getting reset')
    resp = client.post(reverse('account_signup'), {
        # csrf_elem['name']: csrf_elem['value'],
        'email': INITIAL_USER_EMAIL,
        'password1': INITIAL_USER_PASSWORD,
        'password2': INITIAL_USER_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, (
        'Error, signup with follow=True should have returned response code 200 and the verification sent page')
    assert CustomUser.objects.filter(
        email=INITIAL_USER_EMAIL).exists(), 'Error, user was not created after successful signup'
    assert not resp.wsgi_request.user.is_authenticated, (
        'Error, CustomUser was authenticated after signup before email confirmation and login')

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.find(
        'h2').get_text() == 'Verify Your Email Address', (
        'Error, successful signup did not land at the Verify Email page')

    # --------------------------------------------------------------------
    logger.debug('get the email confirmation url from the email just sent')
    assert len(mail.outbox) == email_pointer + 1, (
        'Error, Email outbox length is not larger after successful signup')
    assert mail.outbox[email_pointer].to == [INITIAL_USER_EMAIL]
    assert mail.outbox[email_pointer].from_email == 'root@localhost'
    assert 'Please Confirm Your Email Address' in mail.outbox[email_pointer].subject, (
        'Error, subject of email confirmation mismatch')
    assert 'To confirm this is correct,' in mail.outbox[email_pointer].body, (
        'Error, text in email mismatch')
    # logger.debug(f'body of first message: {mail.outbox[email_pointer].body}')
    confirm_url = get_url_from_email_body(mail.outbox[email_pointer].body)
    logger.debug(f'*** confirm_url: {confirm_url}')

    # --------------------------------------------------------------------
    logger.debug('get custom user just created')
    sup_user = CustomUser.objects.get(email=INITIAL_USER_EMAIL)
    assert sup_user.email == INITIAL_USER_EMAIL, (
        'Error, Email is different than requested')

    # --------------------------------------------------------------------
    logger.debug('get email confirmation form using link from email')
    resp = client.get(confirm_url)
    assert resp.status_code == 200, (
        'Error, email confirmation link/url returned an error')
    assert not resp.wsgi_request.user.is_authenticated, (
        'Error, CustomUser was authenticated after signup before email confirmation and login')
    soup = BeautifulSoup(resp.content, 'html.parser')
    logger.debug(f'page: {soup}')
    assert 'Confirm Email Address' in soup.find('h1').get_text(), (
        'Error, we are not on the Confirm Email page page')
    """.. todo:: have url from email confirmation page email message to use templates/_base.html"""
    form_elem = soup.find('form')
    logger.debug(f'form: {form_elem}')
    button_elem = form_elem.find('button')
    # logger.debug(f'button_elem: {button_elem}')
    assert 'Confirm' in button_elem.get_text(), (
        'Error, unable to find confirm button on what should be the email confirmation page')
    form_action = form_elem['action']
    # logger.debug(f'form_action: {form_action}')
    # assert 'confirm-email' in form_action
    # csrf_elem = form_elem.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    # assert csrf_elem is not None, (
    #     'Error, cannot find csrf token')
    # assert csrf_elem['name'] == 'csrfmiddlewaretoken', (
    #     'Error getting csrf token')
    # # logger.debug(f'csrf_elem: {csrf_elem}')

    # --------------------------------------------------------------------
    logger.debug('post email confirmation')
    resp = client.post(form_action, {
        # csrf_elem['name']: csrf_elem['value'],
    }, follow=True)
    assert resp.status_code == 200, 'Error, confirmation post returned an error'
    assert not resp.wsgi_request.user.is_authenticated, (
        'Error, CustomUser was authenticated after signup before email confirmation and login')
    is_valid, err_str = is_user_email_validated(sup_user)
    assert is_valid, f'Error, user email confirmation did not work with error: {err_str}'
    soup = BeautifulSoup(resp.content, 'html.parser')
    assert soup.find('h2').get_text() == 'Log in', (
        'Error, we are not on the login page after posting email confirmation successfully')

    # --------------------------------------------------------------------
    logger.debug('*** get login page using link as seen in Home page.')
    resp = client.get('/accounts/login/')
    assert resp.status_code == 200, 'Error, get login page failed'
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.h2.get_text() == 'Log in', (
        'Error, should be at the Log in Page')
    # form_elem = soup.find('form')
    # csrf_elem = form_elem.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    # assert csrf_elem is not None
    # assert csrf_elem['name'] == 'csrfmiddlewaretoken', 'Error getting csrf token'
    # # print(f'csrf token: {soup.find('form').find('input', attrs={'name': 'csrfmiddlewaretoken'})["value"]}')

    # --------------------------------------------------------------------
    logger.debug('attempt to login to newly created and verified account')
    resp = client.post('/accounts/login/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'email': INITIAL_USER_EMAIL,
        'password': INITIAL_USER_PASSWORD,
    }, follow=True)

    assert resp.status_code == 200, 'Error, login page did not return 200 OK'

    '''see testing login issue item
        
        Notes::
        
            - `see testing login issue item in this link </docs/build/testing_guide.html#automated-tests-todo-items>`_
            - debug issue with logging in CustomUsers in pytest client post tests
            - client_no_csrf fixture made no difference (see tests/conftest.py)
            - user was created and login with the same constant password
            - it seems that all code to pass csrf tokens should be able to be removed (wait till problem is solved)
            - the email was verified by posting the email url (and confirmed with accounts/conftest.py:is_user_email_validated)
            - maybe there is an undocumented security feature that interferes with testing the login function
            - currently using `client.force_login(sup_user)` to test code that requires the user to be logged in
        
        .. code-block:: python
        
            # Error. testing login post does not authenticate user, and keeps user at login page.
            assert resp.wsgi_request.user.is_authenticated, (
                'User should be authenticated')
            soup = BeautifulSoup(resp.content, 'html.parser')
            logger.debug(f'page: {soup}')
            # confirm we are on the home page
            assert soup.find('h2').get_text() == 'Home', 'Error, we are not on the home page'
            # confirm we have change password and logout links available
            assert len(elem_menu.find('a', href='/accounts/password/change/')) == 1, (
                'Should be logged in showing Password Change Button')
            assert len(elem_menu.find('a', href='/accounts/logout/')) == 1, (
                'Should be logged in showing Logout Button')
            assert elem_menu.find('a', href='/accounts/login/') is None, (
                'Should be logged and not showing Login Button')
            assert elem_menu.find('a', href='/accounts/signup/') is None, (
                'Should be logged and not showing Signup Button')
    '''

    # --------------------------------------------------------------------
    # force login of user
    client.force_login(sup_user)

    # --------------------------------------------------------------------
    # get home page for logged in user
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting home page after force_login')
    assert resp.wsgi_request.user.is_authenticated, (
        'Error, User is not authenticated after force_login')
    # # parse the html response
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'home page: {soup}')
    assert soup.find('h2').get_text() == 'Home', (
        'Error, we are not on the Home page')
    # confirm logged in and shows welcome email address (no first and last name given yet)
    elem_menu = soup.find(id='topSysMenu')
    logger.debug(f'*** elem_menu: {elem_menu}')
    pg_name_email = soup.find(id='tsm_name_email')
    logger.debug(f'pg_name_email: {pg_name_email.text}')
    # confirm the navigation bar has two items - (password change and logout)
    assert len(elem_menu.find('a', href='/accounts/logout/')) == 1, (
        'Error, Should be logged in showing Logout Button')
    assert elem_menu.find('a', href='/accounts/login/') is None, (
        'Error, Should be logged and not showing Login Button')
    assert elem_menu.find('a', href='/accounts/signup/') is None, (
        'Error, Should be logged and not showing Signup Button')
    assert elem_menu.find(id='tsm_name_email').get_text() == INITIAL_USER_EMAIL, (
        'Error, Should be logged in showing user email')


#############################################################################
@pytest.mark.django_db
def test_custom_user_pwd_change_client(get_init_user):
    logger = logging.getLogger(__name__)
    logger.debug(f'*** {__name__}::test_custom_user_change_pwd_client - Starting')
    sup_user = get_init_user
    client = Client()

    # --------------------------------------------------------------------
    logger.debug('force user login')
    client.force_login(sup_user)

    # --------------------------------------------------------------------
    logger.debug('*** get Home page for logged in user.')
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200, (
        'get home page after force_login errored')
    assert resp.wsgi_request.user.is_authenticated, (
        'User is not authenticated after force_login')
    assert CustomUser.objects.count() > 0, (
        'Error, Starting without any CustomUser records')

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.find('h2').get_text() == 'Home', (
        'Error, did not get to Home page')
    elem_menu = soup.find(id='topSysMenu')
    pg_name_email = elem_menu.find(id='tsm_name_email').get_text()
    logger.debug(f'pg_name_email: {pg_name_email}')
    assert pg_name_email == f'{sup_user.first_name} {sup_user.last_name}', (
        'Error, not showing user email address, must not be logged in')
    # confirm the navigation bar has two items - (password change and logout)
    assert len(elem_menu.find('a', href='/accounts/password/change/')) == 1, (
        'Should be logged in showing Password Change Button')
    assert len(elem_menu.find('a', href='/accounts/logout/')) == 1, (
        'Should be logged in showing Logout Button')
    assert elem_menu.find('a', href='/accounts/login/') is None, (
        'Should be logged and not showing Login Button')
    assert elem_menu.find('a', href='/accounts/signup/') is None, (
        'Should be logged and not showing Signup Button')

    # --------------------------------------------------------------------
    logger.debug('get password change form from password change page')
    resp = client.get('/accounts/password/change')
    assert resp.status_code == 301, (
        'Error, did not get 301 permanent redirect from password change page')

    resp = client.get('/accounts/password/change', follow=True)
    assert resp.status_code == 200, (
        'Error, did not get 200 ok on password change redirect/follow')

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.find('h2').get_text() == 'Change Password', (
        'Error, did not get to Change Password page')
    # form_elem = soup.find('form')
    # # logger.debug(f'form: {form_elem}')
    # csrf_elem = form_elem.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    # assert csrf_elem is not None
    # assert csrf_elem['name'] == 'csrfmiddlewaretoken', 'Error getting csrf token'
    # # print(f'csrf token: {soup.find('form').find('input', attrs={'name': 'csrfmiddlewaretoken'})["value"]}')

    # --------------------------------------------------------------------
    logger.debug('post password change with invalid old password failure confirmation')
    resp = client.post('/accounts/password/change/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'oldpassword': 'invalid_password',
        'password1': 'newSimple#123',
        'password2': 'newSimple#123',
    }, follow=True)
    assert resp.status_code == 200, (
        'Error, password change page did not successfully forward to home page')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'soup: {soup}')
    assert soup.find('h2').get_text() == 'Change Password', (
        'Error, we are not on the Change Password page')
    assert soup.find(id='error_1_id_oldpassword').get_text() == 'Please type your current password.', (
        'Error, we are missing the error message on the Current Password field')
    # form_elem = soup.find('form')
    # # logger.debug(f'form: {form_elem}')
    # csrf_elem = form_elem.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    # assert csrf_elem is not None
    # assert csrf_elem['name'] == 'csrfmiddlewaretoken', 'Error getting csrf token'
    # # print(f'csrf token: {soup.find('form').find('input', attrs={'name': 'csrfmiddlewaretoken'})["value"]}')

    # --------------------------------------------------------------------
    logger.debug('post password change with mismatched passwords failure confirmation')
    resp = client.post('/accounts/password/change/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'oldpassword': INITIAL_USER_PASSWORD,
        'password1': 'newSimple#123',
        'password2': 'invalid_password',
    }, follow=True)
    assert resp.status_code == 200, (
        'Error, password change page did not successfully forward to home page')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'soup: {soup}')
    assert soup.find('h2').get_text() == 'Change Password', (
        'Error, we are not on the Change Password page')
    assert soup.find(id='error_1_id_password2').get_text() == 'You must type the same password each time.', (
        'Error, we are missing the error message on the Current Password field')
    # form_elem = soup.find('form')
    # # logger.debug(f'form: {form_elem}')
    # csrf_elem = form_elem.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    # assert csrf_elem is not None
    # assert csrf_elem['name'] == 'csrfmiddlewaretoken', 'Error getting csrf token'
    # # print(f'csrf token: {soup.find('form').find('input', attrs={'name': 'csrfmiddlewaretoken'})["value"]}')

    # --------------------------------------------------------------------
    logger.debug('successful account password change post')

    # get current length of email outbox, which is also a zero relative pointer
    email_pointer = len(mail.outbox)
    #
    # print(f'sup_user: {sup_user:detail}')
    # resp = client.post('/accounts/password/change/', {
    #     csrf_elem['name']: csrf_elem['value'],  # csrf token
    #     'oldpassword': INITIAL_USER_PASSWORD,
    #     'password1': 'newSimple#123',
    #     'password2': 'newSimple#123',
    # })
    # assert resp.status_code == 302, (
    #     'Successful password change did not send 302')
    # logger.debug(f'resp.url: {resp.url}')
    # soup = BeautifulSoup(resp.content, 'html.parser')
    # assert soup.find('h2').get_text() == 'Home', 'Error, we are not on the home page'

    email_pointer = len(mail.outbox)

    print(f'sup_user: {sup_user:detail}')
    resp = client.post('/accounts/password/change/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'oldpassword': INITIAL_USER_PASSWORD,
        'password1': 'newSimple#123',
        'password2': 'newSimple#123',
    }, follow=True)

    assert resp.status_code == 200, 'Error, password change page did not return 200'
    # # parse the html response
    soup = BeautifulSoup(resp.content, 'html.parser')
    logger.debug(f'page: {soup}')
    # Note, we are still on the Change Password page regardless of success or failure
    assert soup.find('h2').get_text() == 'Change Password', (
        'Note: we still on the Change Password page')

    assert len(mail.outbox) == email_pointer, 'Error, Email is not sent on password change success'
    # form_elem = soup.find('form')
    # # logger.debug(f'form: {form_elem}')
    # csrf_elem = form_elem.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    # assert csrf_elem is not None
    # assert csrf_elem['name'] == 'csrfmiddlewaretoken', 'Error getting csrf token'
    # # print(f'csrf token: {soup.find('form').find('input', attrs={'name': 'csrfmiddlewaretoken'})["value"]}')

    # --------------------------------------------------------------------
    logger.debug('*** get Home page to see if still logged in.')
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting home page')
    assert resp.wsgi_request.user.is_authenticated, (
        'User should be authenticated')

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'soup: {soup}')
    assert soup.h1.get_text() == 'Healthy Meals: Diet Assistant', (
        'Error, should be at the Healthy Meals site')
    assert soup.h2.get_text() == 'Home', (
        'Error, should be at Healthy Meals Home Page')
    assert len(soup.find('a', href='/accounts/logout/')) == 1, (
        'Should be logged in showing Logout Button')

    # --------------------------------------------------------------------
    # log out logged in user
    resp = client.get('/accounts/logout/')
    assert resp.status_code == 200, (
        'Error, get logout page should not work')
    assert resp.wsgi_request.user.is_authenticated, (
        'Error, User was logged out after get logout')

    resp = client.post('/accounts/logout/', follow=True)
    assert resp.status_code == 200, (
        'Error, post logout (follow) did not return 200 OK')
    assert not resp.wsgi_request.user.is_authenticated, (
        'Error, user is still logged in after post logout')

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'home page: {soup}')
    # confirm logged out and at home page as logged out
    assert soup.find('h2').get_text() == 'Home'
    elem_menu = soup.find(id='topSysMenu')
    assert soup.find(id='tsm_friend').get_text() == 'Friend'

    # --------------------------------------------------------------------
    logger.debug('*** get Home page to confirm logged out.')
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting home page')
    assert not resp.wsgi_request.user.is_authenticated, (
        'User should not be authenticated')

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'soup: {soup}')
    assert soup.h2.get_text() == 'Home', (
        'Error, should be at the Home Page')
    assert soup.find(id='tsm_friend').get_text() == 'Friend', (
        'Error, home page does not show friend, we should not be logged in')
    assert len(elem_menu.find('a', href='/accounts/login/')) == 1, (
        'Error, should not be logged in and should not show Login link')

    # --------------------------------------------------------------------
    logger.debug('*** get login page using link as seen in Home page.')
    resp = client.get('/accounts/login/')
    assert resp.status_code == 200, 'Error, get login page failed'

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.h2.get_text() == 'Log in', (
        'Error, should be at the Log in Page')

    '''.. todo:: confirm that password changes work in pytest in test_custom_user_pwd_change_client'''

    # # --------------------------------------------------------------------
    # # confirm password change was successful
    # # see if login is successful
    # resp = client.post('/accounts/login/', {
    #     csrf_elem['name']: csrf_elem['value'],  # csrf token
    #     'email': INITIAL_USER_EMAIL,
    #     # 'password': 'newSimple#123',
    #     'password': INITIAL_USER_PASSWORD,
    # }, follow=True)
    #
    # assert resp.wsgi_request.user.is_authenticated, (
    #     'User should be authenticated')
    # # confirm response returns 200 OK
    # assert resp.status_code == 200, 'Error, login page did not return 200 OK'
    # # parse the html response
    # soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    # # confirm we are on the home page
    # assert soup.find('h2').get_text() == 'Home', 'Error, we are not on the home page'
    # # confirm we have change password and logout links available
    # assert len(elem_menu.find('a', href='/accounts/password/change/')) == 1, (
    #     'Should be logged in showing Password Change Button')
    # assert len(elem_menu.find('a', href='/accounts/logout/')) == 1, (
    #     'Should be logged in showing Logout Button')
    # assert elem_menu.find('a', href='/accounts/login/') is None, (
    #     'Should be logged and not showing Login Button')
    # assert elem_menu.find('a', href='/accounts/signup/') is None, (
    #     'Should be logged and not showing Signup Button')


#############################################################################
@pytest.mark.django_db
def test_custom_user_pwd_reset_client(get_init_user):
    logger = logging.getLogger(__name__)
    logger.debug(f'*** {__name__}::test_custom_user_pwd_reset_client - Starting')
    sup_user = get_init_user
    client = Client()

    # client.force_login(sup_user)
    # resp = client.get(reverse("home"))
    # # confirm response is OK
    # assert resp.status_code == 200, 'get home page after force_login errored'
    # assert resp.wsgi_request.user.is_authenticated, 'User is not authenticated after force_login'
    assert CustomUser.objects.count() > 0, (
        'Error, Starting without any CustomUser records')

    # --------------------------------------------------------------------
    logger.debug('*** get password reset page for form')
    resp = client.get('/accounts/password/reset')
    assert resp.status_code == 301, (
        'Error, did not get 301 permanent redirect, is follow=True not needed?')

    resp = client.get('/accounts/password/reset', follow=True)
    assert resp.status_code == 200, (
        'Error, get password change redirected/followed page not 200 - OK')

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    h2_elem = soup.find('h2').get_text()
    logger.debug(f'h2_elem: {h2_elem}')
    assert h2_elem == 'Password Reset', (
        'Error, did not get to Password Reset page')
    # form_elem = soup.find('form')
    # # logger.debug(f'*** get password/reset form: {form_elem}')
    # csrf_elem = form_elem.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    # assert csrf_elem is not None, (
    #     'Error, did not find csrf token')
    # assert csrf_elem['name'] == 'csrfmiddlewaretoken', (
    #     'Error getting csrf token')

    # --------------------------------------------------------------------
    logger.debug('*** account password reset post with email message')

    # get length of email outbox
    email_pointer = len(mail.outbox)  # length of email messages list, also zero relative pointer
    assert email_pointer == 0, 'Email outbox length does not start at 0'

    # confirm post the password reset is forwarded
    resp = client.post('/accounts/password/reset/', {
        # csrf_elem['name']: csrf_elem['value'],
        'email': INITIAL_USER_EMAIL,
    })
    assert resp.status_code == 302, 'Error, login page did not redirect password reset'

    # post the password reset
    resp = client.post('/accounts/password/reset/', {
        # csrf_elem['name']: csrf_elem['value'],
        'email': INITIAL_USER_EMAIL,
    }, follow=True)
    # confirm response is successful
    assert resp.status_code == 200, 'Error, login page did not successfully redirected to password reset done page'

    # parse the html response
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'*** post password/reset email page: {soup}')
    h2_elem = soup.find('h2').get_text()
    logger.debug(f'h2_elem: {h2_elem}')
    assert h2_elem == 'Password Reset Done', 'Error, did not get to Password Reset Done page'
    assert 'We have sent you an e-mail.' in soup.find(
        id='pwd_reset_done').get_text(), 'Error, missing we have sent you an e-mail'

    # assert len(mail.outbox) == email_pointer + 1, 'Error, Email outbox length is not larger after successful password reset'
    assert mail.outbox[email_pointer].to == [INITIAL_USER_EMAIL]
    assert mail.outbox[email_pointer].from_email == 'root@localhost'
    assert 'Password Reset E-mail' in mail.outbox[email_pointer].subject
    logger.debug(f'body of email message: {mail.outbox[email_pointer].body}')
    assert 'click the button below to reset your password.' in mail.outbox[
        email_pointer].body, 'Error, reset password message difference'

    confirm_url = get_url_from_email_body(mail.outbox[email_pointer].body)
    logger.debug(f'confirm_url: {confirm_url}')

    # --------------------------------------------------------------------
    logger.debug('get custom user password reset form from link in email')

    resp = client.get(confirm_url)
    assert resp.status_code == 302, 'Error, email password reset did no do a 302 forward'
    resp_url = resp.url
    logger.debug(f'resp.url: {resp_url}')
    # Note, we need to do a regular expression, because it seems there is a sequence number in the URL
    assert re.compile(r'/accounts/password/reset/key/.*-set-password/').search(
        resp_url), 'Error, Need to know the url to post to'

    resp = client.get(resp_url)
    assert resp.status_code == 200, 'Error, email password reset doing a second 302 forward'
    resp = client.get(resp_url, follow=True)
    assert resp.status_code == 200, f'Error, email client.get password reset ({confirm_url}) returned an error'
    assert not resp.wsgi_request.user.is_authenticated, 'Error, CustomUser was authenticated after signup before email confirmation and login'
    # parse the html response
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    form_elem = soup.find('form')
    logger.debug(f'form: {form_elem}')
    button_elem = form_elem.find('button')
    logger.debug(f'button_elem: {button_elem}')
    assert 'Change Password' in button_elem.get_text(), 'Error, unable to find Change Password button on email'
    # form_action = form_elem['action']
    # # logger.debug(f'form_action: {form_action}')
    # assert '.' == form_action
    # csrf_elem = form_elem.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    # assert csrf_elem is not None, 'Error, we could not find the csrf token'
    # assert csrf_elem['name'] == 'csrfmiddlewaretoken', 'Error getting csrf token'

    # --------------------------------------------------------------------
    logger.debug('post the custom user password reset from form')

    resp = client.post(resp_url, {
        # csrf_elem['name']: csrf_elem['value'],
        'password1': 'newSimple#123',
        'password2': 'newSimple#123',
    }, follow=True)
    assert resp.status_code == 200, 'Error, confirmation post returned an error'
    assert not resp.wsgi_request.user.is_authenticated, 'Error, CustomUser was authenticated after signup before email confirmation and login'
    # parse the html response
    soup = BeautifulSoup(resp.content, 'html.parser')
    logger.debug(f'home page: {soup}')
    assert soup.find('h2').get_text() == 'Change Password Done'

    '''.. todo:: confirm that password changes work in pytest in test_custom_user_pwd_change_client'''

    # # --------------------------------------------------------------------
    # # confirm password change was successful
    # # unable to successfully test login, so trying an invalid password change to confirm password is updated
    # # post an account password change using original old password (should now be invalid if the change took place)
    # form_elem = soup.find('form')
    # # logger.debug(f'form: {form_elem}')
    # csrf_elem = form_elem.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    # assert csrf_elem is not None
    # assert csrf_elem['name'] == 'csrfmiddlewaretoken', 'Error getting csrf token'
    # # logger.debug(f'csrf_elem: {csrf_elem}')
    # resp = client.post('/accounts/login/', {
    #     # csrf_elem['name']: csrf_elem['value'], # csrf token
    #     'oldpassword': INITIAL_USER_PASSWORD,
    #     'password1': 'newSimple#123',
    #     'password2': 'newSimple#123',
    # }, follow=True)
    # # confirm response is forwarded to home page
    # assert resp.status_code == 200, 'Error, login page did not successfully forward to home page'
    # # # parse the html response
    # soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    # # confirm we are on the home page
    # assert soup.find('h2').get_text() == 'Home', 'Error, we are not on the home page'
    #
    # logger = logging.getLogger(__name__)
    # logger.debug(f'***  {__name__} test_custom_user_pwd_reset_client - started')
    # logger.debug(f'*** {__name__}::test_custom_user_pwd_reset_client - Starting')
    # sup_user = get_init_user
    # client = Client()
    #
    # # --------------------------------------------------------------------
    # # post account password
    # resp = client.get('/accounts/password/reset') # /accounts/password/set
    # assert resp.status_code == 200, 'Error, get password reset page not 200 OK'
    #
    # # # parse the html response
    # soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    # assert resp.status_code == 999, 'Debugging, stop here'
    #
    # '''.. todo:: confirm that password changes work in pytest in test_custom_user_pwd_change_client'''

    # # --------------------------------------------------------------------
    # accounts/password/reset/key.  Is this needed?
    #    email sent with link to PasswordResetFromKeyView view
