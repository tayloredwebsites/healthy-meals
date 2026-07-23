import re
import sys
from http.client import HTTPResponse
from os import abort

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

from accounts.helpers import is_user_email_valid, validate_user_email, is_user_valid
from accounts.models import CustomUser
from allauth.account.models import EmailAddress

from tests.accounts.conftest import get_url_from_email_body
# from tests.accounts.conftest import truncate_custom_users
from tests.accounts.factories import CustomUserFactory

import logging

logger = logging.getLogger(__name__)

from tests.conftest import soup_screenshot
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


#############################################################################
@pytest.mark.django_db
def test_user_rest_signup():  # get_super_user):
    logger.debug('info%s::test_custom_user_signup - Starting', __name__)
    client = Client()

    assert CustomUser.objects.count() == 0, (
        'There should be no CustomUser instances')

    # --------------------------------------------------------------------
    logger.info('+++ get Home page, and validate home page header links for logged out user.')
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting home page')
    assert not resp.wsgi_request.user.is_authenticated, (
        'User should not be authenticated')
    soup = BeautifulSoup(resp.content, 'html.parser')
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
        'Error, Logged out user should show Password Reset link')

    # --------------------------------------------------------------------
    logger.info('\n********************************************************')
    logger.info('Start Signup Process (test_user_rest.py::test_user_rest_signup)\n')
    logger.info(f'+++ get signup page for form')
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
    logger.info('+++ post account signup for user to fail with mismatched password')
    resp = client.post(reverse('account_signup'), {
        # csrf_elem['name']: csrf_elem['value'],
        'email': REGUSER_EMAIL,
        'password1': INITIAL_PASSWORD,
        'password2': BAD_PASSWORD,
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
    logger.info('+++ post account signup for user to fail with password too simple')
    resp = client.post(reverse('account_signup'), {
        # csrf_elem['name']: csrf_elem['value'],
        'email': REGUSER_EMAIL,
        'password1': BAD_PASSWORD,
        'password2': BAD_PASSWORD,
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
    logger.info('+++ post account signup for user with good password, Note: pytest does not need csrf token!')
    # get current length of email outbox, which is also a zero relative pointer
    email_pointer = len(mail.outbox)
    assert email_pointer == 0, (
        'Email outbox length does not start at 0, database is not getting reset')
    resp = client.post(reverse('account_signup'), {
        # csrf_elem['name']: csrf_elem['value'],
        'email': REGUSER_EMAIL,
        'password1': INITIAL_PASSWORD,
        'password2': INITIAL_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, (
        'Error, signup with follow=True should have returned response code 200 and the verification sent page')
    initial_user_rec = CustomUser.objects.get(email=REGUSER_EMAIL)
    assert initial_user_rec is not None, (
        'Error, user was not created after successful signup')
    is_valid, err_str, ret_dict = is_user_email_valid(initial_user_rec)
    assert not is_valid, (
        'Error, user should not be validated after signup, but is.')
    assert not resp.wsgi_request.user.is_authenticated, (
        'Error, CustomUser was authenticated after signup before "Verify Email" and login')

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.find(
        'h2').get_text() == 'Verify Your Email Address', (
        'Error, successful signup did not land at the Verify Email page')

    # --------------------------------------------------------------------
    logger.info('+++ get login page using link as seen in Home page.')
    resp = client.get('/accounts/login/')
    assert resp.status_code == 200, 'Error, get login page failed'
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.h2.get_text() == 'Log in', (
        'Error, should be at the Log in Page')

    # --------------------------------------------------------------------
    logger.info('+++ attempt and fail to log in without email validation')
    resp = client.post('/accounts/login/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'login': REGUSER_EMAIL,
        'password': INITIAL_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, (
        'Error, signup with follow=True should have returned response code 200 and the verification sent page')

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.find(
        'h2').get_text() == 'Verify Your Email Address', (
        'Error, successful signup did not land at the Verify Email page')
    assert not resp.wsgi_request.user.is_authenticated, (
        'Error, CustomUser was authenticated after signup before "Verify Email" and login')
    assert len(elem_menu.find('a', href='/accounts/login/')) == 1, (
        'Error, should not be logged in and should not show Login link')

    # --------------------------------------------------------------------
    logger.info('+++ get the "Verify Email" url from the email just sent')
    assert len(mail.outbox) == email_pointer + 1, (
        'Error, Email outbox length is not larger after successful signup')
    email_sent = mail.outbox[email_pointer]
    assert email_sent.to == [REGUSER_EMAIL]
    assert email_sent.from_email == 'root@localhost'
    assert 'Please Confirm Your Email Address' in email_sent.subject, (
        'Error, subject of "Verify Email" mismatch')
    assert 'To confirm this is correct,' in email_sent.body, (
        'Error, text in "Verify Email" mismatch')
    # logger.debug(f'body of first message: {email_sentbody}')
    confirm_url = get_url_from_email_body(email_sent.body)
    logger.debug('+++ confirm_url: %s', confirm_url)

    # --------------------------------------------------------------------
    logger.info('+++ get custom user just created')
    reg_user = CustomUser.objects.get(email=REGUSER_EMAIL)
    assert reg_user.email == REGUSER_EMAIL, (
        'Error, Email is different than requested')

    # --------------------------------------------------------------------
    logger.info('+++ get "Verify Email" form using link from email')
    resp = client.get(confirm_url)
    assert resp.status_code == 200, (
        'Error, "Verify Email" link/url returned an error')
    assert not resp.wsgi_request.user.is_authenticated, (
        'Error, CustomUser was authenticated after signup before "Verify Email" and login')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert 'Confirm Email Address' in soup.find('h1').get_text(), (
        'Error, we are not on the "Verify Email" page')
    form_elem = soup.find('form')
    # logger.debug(f'form: {form_elem}')
    button_elem = form_elem.find('button')
    # logger.debug(f'button_elem: {button_elem}')
    assert 'Confirm' in button_elem.get_text(), (
        'Error, unable to find confirm button on what should be the "Verify Email" page')
    form_action = form_elem['action']

    # --------------------------------------------------------------------
    logger.info('+++ post "Verify Email" url')
    resp = client.post(form_action, {
        # csrf_elem['name']: csrf_elem['value'],
    }, follow=True)
    assert resp.status_code == 200, 'Error, "Verify Email" post returned an error'
    assert not resp.wsgi_request.user.is_authenticated, (
        'Error, CustomUser was authenticated after signup before "Verify Email"n and login')
    is_valid, err_str, ret_dict = is_user_email_valid(reg_user.email, reg_user)
    assert is_valid, f'Error, "Verify Email" did not work with error: {err_str}'
    soup = BeautifulSoup(resp.content, 'html.parser')
    assert soup.find('h2').get_text() == 'Log in', (
        'Error, we are not on the login page after posting "Verify Email" successfully')

    # --------------------------------------------------------------------
    logger.info('+++ log in user.')
    resp = client.post('/accounts/login/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'login': REGUSER_EMAIL,
        'password': INITIAL_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, 'Error, login page did not return 200 OK'
    soup = BeautifulSoup(resp.content, 'html.parser')

    # --------------------------------------------------------------------
    logger.info('+++ confirm we are on the home page after login.')
    assert soup.find('h2').get_text() == 'Home', (
        'Error, we are not on the Home page')
    elem_menu = soup.find(id='topSysMenu')
    pg_name_email = soup.find(id='tsm_name_email')
    logger.debug('pg_name_email: %s', pg_name_email.text)
    assert elem_menu.find(id='tsm_name_email').get_text() == REGUSER_EMAIL, (
        'Error, Should be logged in showing user email')
    # confirm we have change password and logout links available
    assert len(elem_menu.find('a', href='/accounts/password/change/')) == 1, (
        'Should be logged in showing Password Change Button')
    assert len(elem_menu.find('a', href='/accounts/logout/')) == 1, (
        'Should be logged in showing Logout Button')
    assert elem_menu.find('a', href='/accounts/login/') is None, (
        'Should be logged and not showing Login Button')
    assert elem_menu.find('a', href='/accounts/signup/') is None, (
        'Should be logged and not showing Signup Button')
    assert resp.wsgi_request.user.is_authenticated, (
        'User should be authenticated')
    assert CustomUser.objects.count() == 1, (
        'Error, Starting without any CustomUser records')


#############################################################################
@pytest.mark.django_db
def test_user_rest_change_pwd(get_regular_user):
    logger.info(f'+++ {__name__}::test_user_rest_change_pwd - Starting')

    client = Client()

    # --------------------------------------------------------------------
    logger.info('\n********************************************************')
    logger.info('Start Password Change Process (test_user_rest.py::test_user_rest_change_pwd)\n')
    logger.info('+++ login in regular user., to confirm we can login in with the original password')

    reg_user = get_regular_user

    # code to force login
    client.force_login(reg_user)

    # --------------------------------------------------------------------
    logger.info('+++ get Home page, and confirm user us logged in.')
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting home page')
    assert resp.wsgi_request.user.is_authenticated, (
        'User should be authenticated')

    # --------------------------------------------------------------------
    logger.info('+++ get password change form from password change page')
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
    form_elem = soup.find(id='pwd_change_form')
    # logger.debug(f'form: {form_elem}')
    assert form_elem.find(id='id_oldpassword') is not None, (
        'Error, missing old password field.')
    assert form_elem.find(id='id_password1') is not None, (
        'Error, missing password1 field.')
    assert form_elem.find(id='id_password2') is not None, (
        'Error, missing password2 field.')
    button_elem = form_elem.find('button')
    # logger.debug(f'button_elem: {button_elem}')
    assert 'Change Password' in button_elem.get_text(), (
        'Error, unable to find Change Password button.')
    assert form_elem['action'] == '/accounts/password/change/', (
        'Error, form does not point to the password change url')

    # --------------------------------------------------------------------
    logger.info('+++ post password change with invalid old password failure confirmation')
    resp = client.post('/accounts/password/change/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'oldpassword': BAD_PASSWORD,
        'password1': RESET_PASSWORD,
        'password2': RESET_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, (
        'Error, password change page did not successfully forward to home page')
    soup = BeautifulSoup(resp.content, 'html.parser')
    assert soup.find('h2').get_text() == 'Change Password', (
        'Error, we are not on the Change Password page')
    assert soup.find(id='error_1_id_oldpassword').get_text() == 'Please type your current password.', (
        'Error, we are missing the error message on the Current Password field')

    # --------------------------------------------------------------------
    logger.info('+++ post password change with mismatched passwords failure confirmation')
    resp = client.post('/accounts/password/change/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'oldpassword': INITIAL_PASSWORD,
        'password1': RESET_PASSWORD,
        'password2': BAD_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, (
        'Error, password change page did not successfully forward to home page')
    soup = BeautifulSoup(resp.content, 'html.parser')
    assert soup.find('h2').get_text() == 'Change Password', (
        'Error, we are not on the Change Password page')
    assert soup.find(id='error_1_id_password2').get_text() == 'You must type the same password each time.', (
        'Error, we are missing the error message on the Current Password field')

    # --------------------------------------------------------------------
    logger.info('+++ post a successful account password change')

    # get current length of email outbox, which is also a zero relative pointer
    email_pointer = len(mail.outbox)

    # print(f'reg_user: {reg_user:detail}')
    resp = client.post('/accounts/password/change/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'oldpassword': INITIAL_PASSWORD,
        'password1': RESET_PASSWORD,
        'password2': RESET_PASSWORD,
    }, follow=True)

    assert resp.status_code == 200, 'Error, password change page did not return 200'
    # # parse the html response
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    # Note, we are still on the Change Password page regardless of success or failure
    assert soup.find('h2').get_text() == 'Change Password', (
        'Note: we still on the Change Password page')

    assert len(mail.outbox) == email_pointer, 'Error, Email was sent on password change success'

    # --------------------------------------------------------------------
    logger.info('+++ get Home page to confirm we are still logged in.')
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting home page')
    assert resp.wsgi_request.user.is_authenticated, (
        'User should be authenticated')

    soup = BeautifulSoup(resp.content, 'html.parser')
    assert soup.h1.get_text() == 'Healthy Meals: Diet Assistant', (
        'Error, should be at the Healthy Meals site')
    assert soup.h2.get_text() == 'Home', (
        'Error, should be at Healthy Meals Home Page')
    assert len(soup.find('a', href='/accounts/logout/')) == 1, (
        'Should be logged in showing Logout Button')

    # --------------------------------------------------------------------
    logger.info('+++ log out logged in user.')
    # resp = client.get('/accounts/logout/')
    # assert resp.status_code == 200, (
    #     'Error, get logout page should not work')
    # assert resp.wsgi_request.user.is_authenticated, (
    #     'Error, User was logged out after get logout')
    #
    resp = client.post('/accounts/logout/', follow=True)
    assert resp.status_code == 200, (
        'Error, post logout (follow) did not return 200 OK')
    assert not resp.wsgi_request.user.is_authenticated, (
        'Error, user is still logged in after post logout')

    # --------------------------------------------------------------------
    logger.info('+++ confirm we are on the Home page and logged out.')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'home page: {soup}')
    # confirm logged out and at home page as logged out
    assert soup.find('h2').get_text() == 'Home'
    elem_menu = soup.find(id='topSysMenu')
    assert soup.find(id='tsm_friend').get_text() == 'Friend'
    assert len(elem_menu.find('a', href='/accounts/login/')) == 1, (
        'Error, should not be logged in and should not show Login link')
    assert len(soup.find('a', href='/accounts/password/reset/')) == 1, (
        'Error, Logged out user should show Password Reset link')

    # --------------------------------------------------------------------
    logger.info('+++ log in user.')
    resp = client.post('/accounts/login/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'login': REGUSER_EMAIL,
        'password': RESET_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, (
        'Error, login page did not return 200 OK')
    soup = BeautifulSoup(resp.content, 'html.parser')

    soup_screenshot(soup)

    # --------------------------------------------------------------------
    logger.info('+++ Confirm we are on the home page after login.')
    assert 'Home' in soup.find('h2').get_text(), (
        'Error, we are not on the Home page')

    elem_menu = soup.find(id='topSysMenu')
    pg_name_email = soup.find(id='tsm_name_email')
    logger.debug('pg_name_email: %s', pg_name_email.text)
    assert elem_menu.find(id='tsm_name_email').get_text() == f'{REGUSER_FNAME} {REGUSER_LNAME}', (
        'Error, Should be logged in showing user full name')
    # confirm we have change password and logout links available
    assert len(elem_menu.find('a', href='/accounts/password/change/')) == 1, (
        'Should be logged in showing Password Change Button')
    assert len(elem_menu.find('a', href='/accounts/logout/')) == 1, (
        'Should be logged in showing Logout Button')
    assert elem_menu.find('a', href='/accounts/login/') is None, (
        'Should be logged and not showing Login Button')
    assert elem_menu.find('a', href='/accounts/signup/') is None, (
        'Should be logged and not showing Signup Button')
    assert resp.wsgi_request.user.is_authenticated, (
        'User should be authenticated')
    assert CustomUser.objects.count() == 1, (
        'Error, Starting without any CustomUser records')


#############################################################################
@pytest.mark.django_db
def test_user_rest_reset_pwd(get_regular_user):
    logger.info(f'+++ {__name__}::test_user_rest_reset_pwd - Starting')

    reg_user = get_regular_user
    client = Client()
    # client.force_login(reg_user)

    is_valid, errs, recs_dict = is_user_email_valid(reg_user.email, reg_user)
    if not is_valid:
        is_valid, errs, recs_dict = validate_user_email(reg_user.email, reg_user, recs_dict.get('EmailAddress'))
    assert is_valid, errs
    is_valid, errs, recs_dict = is_user_email_valid(reg_user.email, reg_user)
    assert is_valid, errs

    assert CustomUser.objects.count() == 1, (
        'There should be just one CustomUser instances')

    # --------------------------------------------------------------------
    logger.info('\n********************************************************')
    logger.info('Start Password Reset Process (test_user_rest.py::test_user_rest_reset_pwd)\n')
    logger.info('+++ get Home page, and validate home page header links for logged out user.')
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting home page')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.find('h3').get_text() == 'Home', (
        'Error, did not get to Home page')
    assert soup.find(id='login_link')['href'] == '/accounts/login/', (
        'Error, should not be logged in and should show Login link')
    assert soup.find(id='reset_pwd_link')['href'] == '/accounts/password/reset/', (
        'Error, did not get to Password Reset link')

    # --------------------------------------------------------------------
    logger.info('+++ get password reset page for form')
    # resp = client.get('/accounts/password/reset')
    # assert resp.status_code == 301, (
    #     'Error, did not get 301 permanent redirect, is follow=True not needed?')
    resp = client.get('/accounts/password/reset', follow=True)
    assert resp.status_code == 200, (
        'Error, get password change redirected/followed page not 200 - OK')

    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert soup.find('h2').get_text() == 'Password Reset', (
        'Error, did not get to Password Reset page')
    form_elem = soup.find(id='pwd_reset_form')
    assert form_elem.find(id='id_email') is not None, (
        'Error, missing email field.')
    button_elem = form_elem.find('button')
    assert 'Reset Password' in button_elem.get_text(), (
        'Error, unable to find Reset Password button.')
    assert form_elem['action'] == '/accounts/password/reset/', (
        'Error, form does not point to the password reset url')

    # # --------------------------------------------------------------------
    logger.info('+++ post password reset with email message')

    # get length of email outbox
    email_pointer = len(mail.outbox)  # length of email messages list, also zero relative pointer

    # post the password reset
    resp = client.post('/accounts/password/reset/', {
        # csrf_elem['name']: csrf_elem['value'],
        'email': REGUSER_EMAIL,
    }, follow=True)
    # confirm response is successful
    assert resp.status_code == 200, 'Error, login page did not successfully redirected to password reset done page'

    # parse the html response
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'''************************************************************ post password/reset email page:
    #     {soup}''')
    h2_elem = soup.find('h2').get_text()
    logger.debug('h2_elem: %s', h2_elem)
    assert h2_elem == 'Password Reset Done', 'Error, did not get to Password Reset Done page'
    assert 'We have sent you an e-mail.' in soup.find(
        id='pwd_reset_done').get_text(), 'Error, missing we have sent you an e-mail'

    assert len(mail.outbox) == email_pointer + 1, (
        'Error, Email was not sent on password reset')

    email_sent = mail.outbox[email_pointer]
    logger.debug('+++ email_sent.to: %s', email_sent.to)
    logger.debug('+++ email_sent.from_email: %s', email_sent.from_email)
    logger.debug('+++ email_sent.subject: %s', email_sent.subject)
    logger.debug('+++ email_sent.body:\n%s', email_sent.body)
    assert email_sent.to == [REGUSER_EMAIL]
    assert email_sent.from_email == 'root@localhost'
    assert 'Password Reset E-mail' in email_sent.subject, (
        'Error, Invalid subject in reset password email message')
    assert 'we do not have any record of such an account' not in email_sent.body, (
        'Error, we do not have any record of such an account')
    assert 'click the button below to reset your password.' in email_sent.body, (
        'Error, reset password message difference')

    confirm_url = get_url_from_email_body(email_sent.body)
    logger.debug('confirm_url: %s', confirm_url)
    assert confirm_url.startswith('/accounts/password/reset/key/'), (
        'Error, Confirm URL does not start with /accounts/password/reset/key/')

    # --------------------------------------------------------------------
    logger.info('get custom user password reset/change) form from link provided by the email')

    resp = client.get(confirm_url)
    assert resp.status_code == 302, f'Error, email client.get password reset ({confirm_url}) returned an error'
    # logger.debug(f'resp.url: {resp.url}')  # get the current page after forward (/accounts/password/reset/key/1-set-password/)
    forwarded_reset_url = resp.url
    resp = client.get(confirm_url, follow=True)
    assert resp.status_code == 200, f'Error, email client.get password reset ({confirm_url}) returned an error'
    assert not resp.wsgi_request.user.is_authenticated, 'Error, CustomUser was authenticated after signup before email confirmation and login'
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert 'Change Password' in soup.find('h2').get_text()
    assert 'Change Password' in soup.find('h3').get_text()
    form_elem = soup.find(id='pwd_reset_key_form')
    assert form_elem.find('input', attrs={'name': 'password1'}) is not None, (
        'Error, missing password1 field.')
    assert form_elem.find('input', attrs={'name': 'password2'}) is not None, (
        'Error, missing password2 field.')
    button_elem = form_elem.find('button')
    assert 'Change Password' in button_elem.get_text(), (
        'Error, unable to find Reset Password button.')
    # confirm that form action is to post the curent page
    assert form_elem['action'] == '.', (
        'Error, form does not point to the current directory')

    # --------------------------------------------------------------------
    logger.info('post new passwords to the forwarded page from email url')
    resp = client.post(forwarded_reset_url, {
        'password1': RESET_PASSWORD,
        'password2': RESET_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, (
        f'Error, email client.get password reset ({forwarded_reset_url}) returned an error')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'page: {soup}')
    assert 'Change Password Done' in soup.find('h2').get_text()
    assert 'has been changed.' in soup.find(id='pwd_reset_key_changed').get_text()

    # --------------------------------------------------------------------
    logger.info('+++ log in user.')
    resp = client.post('/accounts/login/', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'login': REGUSER_EMAIL,
        'password': RESET_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, 'Error, login page did not return 200 OK'
    soup = BeautifulSoup(resp.content, 'html.parser')

    # --------------------------------------------------------------------
    logger.info('+++ confirm we are on the home page after login.')
    assert soup.find('h2').get_text() == 'Home', (
        'Error, we are not on the Home page')
    elem_menu = soup.find(id='topSysMenu')
    pg_name_email = soup.find(id='tsm_name_email')
    logger.debug('pg_name_email: %s', pg_name_email.text)
    assert pg_name_email.text == f'{REGUSER_FNAME} {REGUSER_LNAME}', (
        'Error, Should be logged in showing user First and Last Name')
