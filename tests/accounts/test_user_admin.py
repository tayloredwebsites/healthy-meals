import re
import sys
from datetime import datetime
from pprint import pprint

import bs4
import pytest
from allauth.account.models import EmailAddress
from django.test import Client

from django.contrib.admin.sites import AdminSite

from accounts.helpers import is_user_email_valid
from accounts.models import CustomUser
from accounts.admin import CustomUserAdmin

from bs4 import BeautifulSoup

import logging

logger = logging.getLogger(__name__)

from django.db import IntegrityError, transaction

from tests.conftest import soup_screenshot
from django.conf import settings

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
def test_user_admin_create_admin(get_super_user):
    """Test admin interface flow to test CustomUser CRUD (create, read/view, update, soft delete,  and list users.

        .. todo:: test the creation of regular users, who are then changed to superuser, and confirm they have access to the admin interface

            - It seems that to create a test superuser who has access to the admin interface must be created by CustomUser.objects.create_superuser()
            - does this mean that we will not be able to change existing test users to superuser?
            - is there an issue with this in development (or production)?

        .. todo:: set logging level for running nox testing session to error (don't show info messages normally)

        .. todo:: document maximum line length change from 120 to 999 to prevent pycharm formatting statements automatically to allow long descriptions, urls, and paragraph descriptions.
   """
    logger.info(f'+++{__name__}::test_user_admin_create - Starting')
    client = Client()

    # using pytest fixtures to get the superuser user object
    sup_user = get_super_user

    assert CustomUser.objects.count() == 1, (
        'There should be one CustomUser instances for sup_user')
    assert EmailAddress.objects.count() == 1, (
        'There should be one EmailAddress instances for sup_user')

    # --------------------------------------------------------------------
    logger.info('\n********************************************************\nStart Admin User Create Process Testing\n')
    logger.info('+++admin admin home page, parse, & validate elements.')
    resp = client.get('/admin/', follow=True)
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting admin login page')
    assert not resp.wsgi_request.user.is_authenticated, (
        'User should not be authenticated')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'+++admin home page soup: {soup}')
    assert soup.find(id='site-name').get_text() == 'Healthy Meals Admin', (
        'Error, we are missing the admin interface title')
    form_element = soup.find(id='login-form')
    # logger.debug(f'+++admin home page form_elem: {form_element}')
    # skipping check for csrf, as this is by default not checked in tests
    # csrf_elem = form_element.find('input', attrs={'name': 'csrfmiddlewaretoken'})
    assert form_element['action'] == '/admin/login/?next=%2Fadmin%2F', (
        'Error, form should have /admin/login/?next=%2Fadmin%2F for its action')
    assert form_element.find('input', id='id_username')['name'] == 'username', (
        'Error, we are missing the username input field')
    assert form_element.find('input', id='id_password')['name'] == 'password', (
        'Error, we are missing the password input field')
    submit_row_element = form_element.find('div', attrs={'class': 'submit-row'})
    assert submit_row_element.find('input', attrs={'type': 'submit', 'value': 'Log in'}) is not None, (
        'Error, we are missing the login submit input field')

    # --------------------------------------------------------------------
    logger.info('+++post superuser login')
    resp = client.post('/admin/login/?next=%2Fadmin%2F', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'username': SUPERUSER_EMAIL,
        'password': INITIAL_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, (
        'Error posting login form')
    logger.debug('+++resp.redirect_chain: %s', resp.redirect_chain)
    assert resp.redirect_chain[0][0] == '/admin/', (
        'Error, not redirected to login page')

    # --------------------------------------------------------------------
    logger.info('+++confirm that sup_user is authenticated after logging in.')
    assert resp.wsgi_request.user.is_authenticated, (
        'User should be authenticated')

    # --------------------------------------------------------------------
    logger.info('+++validate Admin Header.')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'+++admin home page soup: {soup}')
    tools_element = soup.find(id='user-tools')
    assert SUPERUSER_FNAME in tools_element.get_text(), (
        'Error, we are not logged in as the superuser in the tools bar')
    assert tools_element.find('a', attrs={'href': '/'}).get_text() is not None, (
        'Error, admin toolbar is missing the view site link')
    assert tools_element.find('a', attrs={'href': '/'}).get_text() == 'View site', (
        'Error, admin toolbar is missing the View site link text')
    assert tools_element.find('a', attrs={'href': '/admin/password_change/'}) is not None, (
        'Error, admin toolbar is missing the change password link')
    assert tools_element.find('a', attrs={'href': '/admin/password_change/'}).get_text() == 'Change password', (
        'Error, admin toolbar is missing the Change password link text')
    assert tools_element.find(id='logout-form', attrs={'action': '/admin/logout/'}) is not None, (
        'Error, admin toolbar is missing the logout link')
    assert 'Log out' in tools_element.find(id='logout-form', attrs={'action': '/admin/logout/'}).get_text(), (
        'Error, admin toolbar is missing the logout link text')

    # --------------------------------------------------------------------
    logger.info('+++get the "Healthy Meals Admin" page once logged in.')
    # resp = client.get('/admin/')
    # # confirm response is OK
    # assert resp.status_code == 200, (
    #     'Error getting admin page')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'+++admin home page after login - soup: {soup}')
    # confirm the fields showing in the Accounts (CustomUser) section of the page
    accounts_div = soup.find('div', attrs={'class': 'app-accounts'})
    # logger.debug(f'+++admin home page after login - accounts_div: {accounts_div}')
    # confirm we have the link to the "Custom users" listing page (under the ACCOUNTS section)
    assert accounts_div.find(id='accounts-customuser').find('a')['href'] == ('/admin/accounts/customuser/'), (
        'Error, missing link to Custom users page')
    # confirm we have the link to the custom user add page
    assert accounts_div.find('a', attrs={'class': 'addlink'})['href'] == ('/admin/accounts/customuser/add/'), (
        'Error, missing link to Custom users page')
    # confirm we have the change link, which is also the list page
    assert accounts_div.find('a', attrs={'class': 'changelink'})['href'] == ('/admin/accounts/customuser/'), (
        'Error, missing link to Custom users page')

    # --------------------------------------------------------------------
    logger.info('+++GET the "Add custom user" page & its form.')
    resp = client.get('/admin/accounts/customuser/add/')
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting admin page')
    soup = BeautifulSoup(resp.content, 'html.parser')
    form_element = soup.find(id='customuser_form')
    #
    # soup_screenshot(soup)
    #
    # confirm we are on the Add custom user page
    assert soup.find('h1').get_text() == 'Add custom user', (
        'Error, we are not on the "Add custom user" page')
    # assert "'username' is automatically set to 'email'" in soup.find(id='username_note').get_text(), (
    #     'Error, missing note about username is the same as email')

    # --------------------------------------------------------------------
    logger.info('+++validate fields in the "Add custom user" form.')
    form_element = soup.find(id='customuser_form')
    #
    # soup_screenshot(form_element)
    #
    assert form_element.get("action") is None, (
        'Error, form element should not have an action attribute')
    # confirm we have the username field being asked for (not email field)
    assert form_element.find('input', id='id_username')['name'] == 'username', (
        'Error, we are missing the username input field')
    assert form_element.find('input', id='id_usable_password_0')['checked'] is not None, (
        'Error, the usable password field is missing or not checked')
    # confirm we are asking for the password twice
    assert form_element.find('input', id='id_password1')['name'] == 'password1', (
        'Error, we are missing the password1 input field')
    assert form_element.find('input', id='id_password2')['name'] == 'password2', (
        'Error, we are missing the password1 input field')
    # assert form_element.find('input', id='id_first_name')['name'] == 'first_name', (
    #     'Error, we are missing the first_name input field')
    # assert form_element.find('input', id='id_last_name')['name'] == 'last_name', (
    #     'Error, we are missing the last_name input field')
    # assert form_element.find('input', id='id_is_superuser')['name'] == 'is_superuser', (
    #     'Error, we are missing the is_superuser input field')
    submit_row_element = form_element.find('div', attrs={'class': 'submit-row'})
    logger.debug('+++submit_row_element: %s', submit_row_element)
    assert submit_row_element.find('input', attrs={'type': 'submit', 'class': 'default', 'name': '_save'})['value'] == 'Save', (
        'Error, we are missing the default "SAVE" button')
    assert submit_row_element.find('input', attrs={'type': 'submit', 'name': '_addanother'})['value'] == 'Save and add another', (
        'Error, we are missing the "Save and add another" button')
    assert submit_row_element.find('input', attrs={'type': 'submit', 'name': '_continue'})['value'] == 'Save and continue editing', (
        'Error, we are missing the "Save and continue editing" button')

    assert CustomUser.objects.count() == 1, (
        'There should be one CustomUser instances')
    assert CustomUser.objects.first().email == SUPERUSER_EMAIL, (
        f'Error, Starting user is not {SUPERUSER_EMAIL}')

    # --------------------------------------------------------------------
    logger.info('+++add a custom minimaluser by posting the initial add fields form.')
    resp = client.post('/admin/accounts/customuser/add/', {
        'username': REGUSER_EMAIL,
        'password1': INITIAL_PASSWORD,
        'password2': INITIAL_PASSWORD,
        # 'first_name': REGUSER_FNAME,
        # 'last_name': REGUSER_LNAME,
        # 'is_superuser': 'checked',
        '_save': 'Save',
    }, follow=True)
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error posting admin add user page')
    soup = BeautifulSoup(resp.content, 'html.parser')
    form_element = soup.find(id='customuser_form')

    # get screenshot of the change form page after adding the user, to confirm the fields are correct and the user was added successfully
    # soup_screenshot(soup)

    success_msg_element = soup.select_one('ul.messagelist li.success')
    assert 'was added successfully.' in success_msg_element.get_text(), (
        'Error, we are missing the success message')

    # --------------------------------------------------------------------
    logger.info('+++ confirm the add fields are displaying in the change page.')

    assert form_element.find('input', id='id_username')['value'] == REGUSER_EMAIL, (
        'Error, username in form is not correct')
    assert form_element.select_one("#id_password p strong:-soup-contains('algorithm')") is not None, (
        'Error, password algorithm is not showing')
    assert 'Reset password' in form_element.select_one("#id_password p a[href='../password/']").get_text(), (
        'Error, Reset password button is not showing')
    assert form_element.find(id='id_first_name').get('value') is None, (
        'Error, First name is not empty')
    assert form_element.find(id='id_last_name').get('value') is None, (
        'Error, Last name is not empty')
    assert form_element.find('input', id='id_email')['value'] == REGUSER_EMAIL, (
        'Error, email address in form is not correct')
    assert form_element.select_one("div.field-is_active div.readonly img[alt='True']"), (
        'Error, user is not active')
    assert form_element.select_one("div.field-is_staff div.readonly img[alt='False']"), (
        'Error, user is staff, but should not be')
    # note: cannot get the is_superuser checkbox value in beautiful soup.  See check of the listing page.
    # assert form_element.find(id='id_is_superuser').get('checked') is None, (
    #     'Error, user has the Superuser field/attribute checked')
    # Note: we are saving the last_login and date_joined fields to use in the next post of the change form, since they are needed to properly update the user.
    last_login_date = form_element.find('input', id='id_last_login_0').get('value')
    last_login_time = form_element.find('input', id='id_last_login_1').get('value')
    date_joined_date = form_element.find('input', id='id_date_joined_0').get('value')
    date_joined_time = form_element.find('input', id='id_date_joined_1').get('value')
    """
    .. todo:: Ensure the Active flag is always set to True in the database save() method.
    .. todo:: remove or test the User Groups, User Permissions fields on the change user page.
    """

    # --------------------------------------------------------------------
    logger.info('+++ read in new user from the database.')
    reg_user = CustomUser.objects.get(email=REGUSER_EMAIL)
    # logger.debug(f'+++reg_user: {reg_user:detail}')

    # --------------------------------------------------------------------
    logger.info('+++ finish adding custom superuser by posting change form fields.')
    resp = client.post(f'/admin/accounts/customuser/{reg_user.id}/change/', {
        'username': REGUSER_EMAIL,
        'first_name': REGUSER_FNAME,
        'last_name': REGUSER_LNAME,
        'is_active': 'checked',
        'is_staff': 'checked',
        'is_superuser': 'checked',
        'last_login_0': str(last_login_date or ''),  # fill in value from displayed form, None goes to empty string
        'last_login_1': str(last_login_time or ''),  # fill in value from displayed form, None goes to empty string
        'date_joined_0': str(date_joined_date or ''),  # fill in value from displayed form, None goes to empty string
        'date_joined_1': str(date_joined_time or ''),  # fill in value from displayed form,  None goes to empty string
        '_save': 'Save',
    }, follow=True)
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error posting admin add user page')
    soup = BeautifulSoup(resp.content, 'html.parser')

    # get screenshot of the listing page after changing the new user, to confirm the fields are correct and the user was added successfully
    soup_screenshot(soup)

    assert form_element.select_one('div p.errornote') is None, (
        'Error, There is an error message on the page, but it should not be there.')
    error_elements = form_element.select('fieldset div ul.errorlist')
    assert error_elements == [], (
        f'Error, There should be no error messages on the page, but there are:\n{error_elements}')
    assert 'was changed successfully.' in soup.select_one('ul.messagelist li.success').get_text(), (
        'Error, we are missing the success message')

    # --------------------------------------------------------------------
    logger.info('+++confirm we added a custom superuser and it is in the listing page.')
    assert 'Select custom user to change' in soup.find('h1').get_text(), (
        'ERROR, we are not on the "Custom user listing" page')

    # get the row for the newly added user, by matching the email
    user_link_element = soup.select_one('tbody .field-email a')
    assert REGUSER_EMAIL in user_link_element.get_text(), (
        f"ERROR, email {REGUSER_EMAIL} is not on the listing page, did it get created?")
    user_row_element = user_link_element.parent.parent

    # check the fields in the row for the newly added user
    assert user_row_element.name == 'tr', (
        'ERROR, user_row_element is not on the user listing row element')
    assert REGUSER_FNAME in user_row_element.find(attrs={'class': 'field-first_name'}).get_text(), (
        'ERROR, the first name does not match the expected value')
    assert REGUSER_LNAME in user_row_element.find(attrs={'class': 'field-last_name'}).get_text(), (
        'ERROR, the last name does not match the expected value')
     # note: We can confirm that the user is a superuser because this is not a checkbox field in beautiful soup.
    assert 'True' in user_row_element.find(attrs={'class': 'field-f_superuser'}).get_text(), (
        'ERROR, superuser flag is not set to True')
    assert user_row_element.find(attrs={'class': 'field-f_deleted'}).get_text().strip() == '-', (
        'ERROR, the should not be deleted')
    assert reg_user.updated_at.strftime('%Y-%m-%d') in user_row_element.find(attrs={'class': 'field-f_updated_at'}).get_text(), (
        'ERROR, the updated_at display does not match the database value')
    # sup_user.refresh_from_db()
    assert user_row_element.find(attrs={'class': 'field-f_updated_by'}).get_text() == f'{sup_user.id}', (
        'ERROR, the updated by display does not show the updated by user id')

    # --------------------------------------------------------------------
    logger.info('+++confirm reg_user still needs its email validated.')
    email_valid, err_str, ret_dict = is_user_email_valid(reg_user)
    assert not email_valid, (
        'Error, admin interface validated email immediately after adding user.')


def test_user_admin_change(get_regular_user, get_super_user):
    """test CustomUser change in the admin interface """
    logger.debug('+++%s::test_user_admin_change - Starting', __name__)

    # --------------------------------------------------------------------
    logger.info('\n********************************************************\nStart Admin User Change Process Testing\n')
    logger.info('+++starting with sup_user and reg_user validated with sup_user logged in.')

    reg_user = get_regular_user
    sup_user = get_super_user

    # code to force login
    client = Client()
    client.force_login(sup_user)

    assert CustomUser.objects.count() == 2, (
        'There should be two CustomUser instances (reg_user and sup_user users)')
    assert EmailAddress.objects.count() == 2, (
        'There should be 2 EmailAddress instance (reg_user and sup_user users)')

    # --------------------------------------------------------------------
    logger.info('+++confirm the starting reg_user values on change page).')
    resp = client.get(f'/admin/accounts/customuser/{reg_user.id}/change/')
    # confirm get request is OK
    assert resp.status_code == 200, (
        'Error getting custom user change page for user: {reg_user.id}')
    soup = BeautifulSoup(resp.content, 'html.parser')
    form_element = soup.find(id='customuser_form')
    #
    # soup_screenshot(soup)
    #
    # confirm we are on the Change custom user page
    assert 'Change custom user' in soup.find('h1').get_text(), (
        'Error, we are not on the "Change custom user" page')
    assert soup.find('h1').get_text() == 'Change custom user', (
        'Error, we are not on the "Change custom user" page')
    assert REGUSER_EMAIL in soup.find('h2').get_text(), (
        'Error, we have the wrong user in the header of the Change custom user page')
    form_element = soup.find(id='customuser_form')
    # assert f'{reg_user.id}' in form_element.select_one('.field-id .readonly').get_text(), (
    #     'Error, invalid user id in the form')
    assert form_element.find('input', id='id_email')['value'] == REGUSER_EMAIL, (
        'Error, email address in form is not correct')
    assert form_element.find('input', id='id_username')['value'] == REGUSER_EMAIL, (
        'Error, email address in form is not correct')
    assert REGUSER_FNAME in form_element.find(id='id_first_name').get('value'), (
        'Error, First name is not correct')
    assert REGUSER_LNAME in form_element.find(id='id_last_name').get('value'), (
        'Error, Last name is not correct')
    assert soup.find(id='xtra_is_superuser').get_text() == 'False', (
        'Error,the Superuser field/attribute is not checked')

    # --------------------------------------------------------------------
    logger.info(f'+++ post name changes on regular user - id: {reg_user.id}, email: {REGUSER_EMAIL}.')
    # first save off the values returned in the change form just returned from the get request.
    # print(f'+++ print(settings.DEBUG): {settings.DEBUG}')
    # print(f'+++ print(settings.TESTING): {settings.TESTING}')
    saved_user_form_fields = save_custom_user_change_fields(form_element)
    logger.debug('+++ saved_user_form_fields:')
    pprint(saved_user_form_fields)

    resp = client.post(f'/admin/accounts/customuser/{reg_user.id}/change/', {
        'email': REGUSER_EMAIL,
        'username': REGUSER_EMAIL,
        'first_name': REGUSER_FNAME + '2',
        'last_name': REGUSER_LNAME + '2',
        'date_joined_0': saved_user_form_fields['date_joined_date'],
        'date_joined_1': saved_user_form_fields['date_joined_time'],
        '_save': 'Save',
    }, follow=True)
    soup = BeautifulSoup(resp.content, 'html.parser')
    logger.debug(f'+++ resp.status_code: {resp.status_code}')
    form_element = soup.find(id='customuser_form')
    if form_element is not None:
        # we were returned back to the form, so there is an error
        error_message = form_element.find(class_='errornote')
        assert error_message is None, (
            'Error, Post of admin change user page did not redirect to listing page.')

    # --------------------------------------------------------------------
    logger.info('+++confirm the names of the reg_user have changed in the listing page.')

    # get all the email link elements in the listing page
    user_link_elements = soup.select('tbody .field-email a')

    # find the row for the reg_user
    user_row_element = None
    for user_link_element in user_link_elements:
        if user_link_element.get_text() == REGUSER_EMAIL:
            user_row_element = user_link_element.parent.parent

    # validate the displayed fields for the regular user row
    assert user_row_element is not None, (
        'Error, Unable to find the user email in the listing page')
    assert user_row_element.name == 'tr', (
        'ERROR, user_row_element is not on the user listing row element')
    assert REGUSER_FNAME + '2' in user_row_element.find(attrs={'class': 'field-first_name'}).get_text(), (
        'ERROR, the first name does not match the expected value')
    assert REGUSER_LNAME + '2' in user_row_element.find(attrs={'class': 'field-last_name'}).get_text(), (
        'ERROR, the last name does not match the expected value')
    assert 'False' in user_row_element.find(attrs={'class': 'field-f_superuser'}).get_text(), (
        'ERROR, superuser flag is not set to False')
    assert 'False' in user_row_element.find(attrs={'class': 'field-f_staff'}).get_text(), (
        'ERROR, staff flag is not set to False')
    assert user_row_element.find(attrs={'class': 'field-f_deleted'}).get_text().strip() == '-', (
        'ERROR, the should not be deleted')
    assert datetime.now().strftime('%Y-%m-%d') in user_row_element.find(attrs={'class': 'field-f_updated_at'}).get_text(), (
        'ERROR, the updated_at display does not match the database value')
    assert user_row_element.find(attrs={'class': 'field-f_updated_by'}).get_text() == f'{sup_user.id}', (
        'ERROR, the updated by display does not match the database value')
    resp = client.get(f'/admin/accounts/customuser/{reg_user.id}/change/', follow=True)
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting custom user change page for user: {reg_user.id}')
    soup = BeautifulSoup(resp.content, 'html.parser')
    form_element = soup.find(id='customuser_form')

    soup_screenshot(soup)

    assert 'Change custom user' in soup.find('h1').get_text(), (
        'Error, we are not on the "Change custom user" page')
    assert soup.find('h1').get_text() == 'Change custom user', (
        'Error, we are not on the "Change custom user" page')
    assert REGUSER_EMAIL in soup.find('h2').get_text(), (
        'Error, we have the wrong user in the header of the Change custom user page')
    form_element = soup.find(id='customuser_form')
    # assert f'{reg_user.id}' in form_element.select_one('.field-id .readonly').get_text(), (
    #     'Error, invalid user id in the form')
    assert form_element.find('input', id='id_email')['value'] == REGUSER_EMAIL, (
        'Error, email address in form is not correct')
    assert form_element.find('input', id='id_username')['value'] == REGUSER_EMAIL, (
        'Error, email address in form is not correct')
    assert REGUSER_FNAME in form_element.find(id='id_first_name').get('value'), (
        'Error, First name is not correct')
    assert REGUSER_LNAME in form_element.find(id='id_last_name').get('value'), (
        'Error, Last name is not correct')
    # assert soup.find(id='xtra_is_superuser').get_text() == 'True', (
    #     'Error,the Superuser field/attribute is not checked')
    reset_btn_element = form_element.find(id='email_reset_pwd')

    # --------------------------------------------------------------------
    logger.info(f'+++ post change regular user to superuser - id: {reg_user.id}, email: {REGUSER_EMAIL}.')
    # first save off the values returned in the change form just returned from the get request.
    saved_user_form_fields = save_custom_user_change_fields(form_element)
    logger.debug('+++ saved_user_form_fields:')
    pprint(saved_user_form_fields)

    resp = client.post(f'/admin/accounts/customuser/{reg_user.id}/change/', {
        'email': REGUSER_EMAIL,
        'username': REGUSER_EMAIL,
        'first_name': saved_user_form_fields['first_name'],
        'last_name': saved_user_form_fields['last_name'],
        'date_joined_0': saved_user_form_fields['date_joined_date'],
        'date_joined_1': saved_user_form_fields['date_joined_time'],
        'is_superuser': 'checked',
        '_save': 'Save',
    }, follow=True)
    soup = BeautifulSoup(resp.content, 'html.parser')
    logger.debug(f'+++ resp.status_code: {resp.status_code}')
    form_element = soup.find(id='customuser_form')
    if form_element is not None:
        # we were returned back to the form, so there is an error
        error_message = form_element.find(class_='errornote')
        assert error_message is None, (
            'Error, Post of admin change user page did not redirect to listing page.')

    # --------------------------------------------------------------------
    logger.info('+++confirm the reg_user is now shown as superuser in the listing page.')
    #
    soup_screenshot(soup)
    #
    # get all the email link elements in the listing page
    user_link_elements = soup.select('tbody .field-email a')

    # find the row for the reg_user
    user_row_element = None
    for user_link_element in user_link_elements:
        if user_link_element.get_text() == REGUSER_EMAIL:
            user_row_element = user_link_element.parent.parent

    # validate the displayed fields for the regular user row
    assert user_row_element is not None, (
        'Error, Unable to find the user email in the listing page')
    assert user_row_element.name == 'tr', (
        'ERROR, user_row_element is not on the user listing row element')
    assert REGUSER_FNAME + '2' in user_row_element.find(attrs={'class': 'field-first_name'}).get_text(), (
        'ERROR, the first name does not match the expected value')
    assert REGUSER_LNAME + '2' in user_row_element.find(attrs={'class': 'field-last_name'}).get_text(), (
        'ERROR, the last name does not match the expected value')
    assert 'True' in user_row_element.find(attrs={'class': 'field-f_superuser'}).get_text(), (
        'ERROR, superuser flag is not set to True')
    assert 'True' in user_row_element.find(attrs={'class': 'field-f_staff'}).get_text(), (
        'ERROR, staff flag is not set to True')
    assert user_row_element.find(attrs={'class': 'field-f_deleted'}).get_text().strip() == '-', (
        'ERROR, the should not be deleted')
    assert datetime.now().strftime('%Y-%m-%d') in user_row_element.find(attrs={'class': 'field-f_updated_at'}).get_text(), (
        'ERROR, the updated_at display does not match the database value')
    assert user_row_element.find(attrs={'class': 'field-f_updated_by'}).get_text() == f'{sup_user.id}', (
        'ERROR, the updated by display does not match the database value')

    # --------------------------------------------------------------------
    logger.info('+++confirm we updated the reg_user in the listing page.')
    assert 'Select custom user to change' in soup.find('h1').get_text(), (
        'ERROR, we are not on the "Custom user listing" page')
    user_link_element = soup.select_one('tbody .field-email a')
    assert REGUSER_EMAIL in user_link_element.get_text(), (
        f"ERROR, email {REGUSER_EMAIL} is not on the listing page, did it get created?")
    user_row_element = user_link_element.parent.parent
    assert user_row_element.name == 'tr', (
        'ERROR, user_row_element is not on the user listing row element')
    assert REGUSER_FNAME in user_row_element.find(attrs={'class': 'field-first_name'}).get_text(), (
        'ERROR, the first name does not match the expected value')
    assert REGUSER_LNAME in user_row_element.find(attrs={'class': 'field-last_name'}).get_text(), (
        'ERROR, the last name does not match the expected value')
    assert 'True' in user_row_element.find(attrs={'class': 'field-f_superuser'}).get_text(), (
        'ERROR, superuser flag is not set to True')
    assert user_row_element.find(attrs={'class': 'field-f_deleted'}).get_text().strip() == '-', (
        'ERROR, the should not be deleted')
    assert reg_user.updated_at.strftime('%Y-%m-%d') in user_row_element.find(attrs={'class': 'field-f_updated_at'}).get_text(), (
        'ERROR, the updated_at display does not match the database value')
    assert user_row_element.find(attrs={'class': 'field-f_updated_by'}).get_text() == f'{sup_user.id}', (
        'ERROR, the updated by display does not match the database value')

    """.. todo:: Prevent email address changes, or coding needed to also update the EmailAddress table."""

    # # --------------------------------------------------------------------
    # logger.info('+++Go to the Add (and Validate) email page (which the Add and Validate Email button links to).')
    # resp = client.get('/admin/account/emailaddress/add/')
    # assert resp.status_code == 200, (
    #     'Error, getting custom user add email page')
    # soup = BeautifulSoup(resp.content, 'html.parser')
    # # logger.debug(f'+++listing users - soup: {soup}')
    # assert soup.h1.get_text() == 'Add email address', (
    #     'Error, h1 header element does say this is the Add Email page')
    # form_element = soup.find(id='emailaddress_form')
    # assert form_element.find('input', id='id_user', attrs={'name': 'user'}) is not None, (
    #     'Error, missing User ID field')
    # assert form_element.find('input', id='id_email', attrs={'name': 'email'}) is not None, (
    #     'Error, missing User email field')
    # assert form_element.find('input', id='id_verified', attrs={'name': 'verified'}) is not None, (
    #     'Error, missing User verified flag')
    # assert form_element.find('input', id='id_primary', attrs={'name': 'primary'}) is not None, (
    #     'Error, missing User primary flag')
    # assert form_element.find('input', attrs={'class': 'default', 'type': 'submit', 'name': '_save'}) is not None, (
    #     'Error, missing default save button')
    #
    # --------------------------------------------------------------------
    # logger.info('+++log in as user updated to superuser and confirm access to admin interface.')
    # resp = client.post('/admin/account/emailaddress/add/', {
    #     # csrf_elem['name']: csrf_elem['value'],  # csrf token
    #     'id_user': reg_user.id,
    #     'id_email': reg_user.email,
    #     'id_verified': 'checked',
    #     'id_primary': 'checked',
    # })
    # assert resp.status_code == 200, (
    #     'Error posting login form')
    # soup = BeautifulSoup(resp.content, 'html.parser')
    #
    # # --------------------------------------------------------------------
    # logger.info('+++get and validate the custom user listing page.')
    # resp = client.get('/admin/accounts/customuser/')
    # assert resp.status_code == 200, (
    #     'Error, getting custom user listing page returned an error')
    # soup = BeautifulSoup(resp.content, 'html.parser')
    # # logger.debug(f'+++listing users - soup: {soup}')
    # assert soup.h1.get_text() == 'Select custom user to change', (
    #     'Error, h1 header element does say this is the User listing page')
    # results_element = soup.find(id='result_list')
    #
    # # --------------------------------------------------------------------
    # logger.info('+++validate the newly created user fields in the Custom User listing page.')
    # user_url_element = results_element.find('a', attrs={'href': f'/admin/accounts/customuser/{reg_user.id}/change/'})
    # assert user_url_element is not None, (
    #     'Error, we cannot find the newly created user in the listing page results')
    # user_row = user_url_element.parent.parent
    # assert user_row is not None, (
    #     'Error, we cannot row of the newly created user in the listing page results')
    #
    # assert user_row.find('td', attrs={'class': 'field-first_name'}).get_text() == REGUSER_FNAME, (
    #     'Error, the newly added user is not displaying the correct first name of the user')
    # assert user_row.find('td', attrs={'class': 'field-last_name'}).get_text() == REGUSER_LNAME, (
    #     'Error, the newly added user is not displaying the correct last name of the user')
    # assert user_row.find('td', attrs={'class': 'field-f_superuser'}).get_text() == 'True', (
    #     'Error, the newly added user is not displayed as a superuser')
    # assert user_row.find('td', attrs={'class': 'field-f_deleted'}).get_text() == '-', (
    #     'Error, the newly added user has an invalid deleted field')
    # assert user_row.find('td', attrs={'class': 'field-f_updated_at'}).get_text() == reg_user.updated_at.strftime('%Y-%m-%d'), (
    #     'Error, the newly added user has an invalid updated_at value')
    # assert user_row.find('td', attrs={'class': 'field-f_updated_by'}).get_text() == f'{reg_user.id}', (
    #     'Error, the newly added user has an invalid updated_by value')
    #
    # --------------------------------------------------------------------
    logger.info('+++go to the change user page and confirm it is changed and is now superuser/staff.')
    resp = client.get(f'/admin/accounts/customuser/{reg_user.id}/change/')
    assert resp.status_code == 200, (
        'Error, getting custom user page returned an error')
    soup = BeautifulSoup(resp.content, 'html.parser')
    #
    # soup_screenshot(soup)
    # sys.exit(2)
    #
    assert soup.h1.get_text() == 'Change custom user', (
        'Error, h1 header element does say this is the Change user page')
    assert REGUSER_EMAIL in soup.find('h2').get_text(), (
        'Error, we have the wrong user in the header of the Change custom user page')
    form_element = soup.find(id='customuser_form')
    # logger.debug(f'''*****************************************************************************************
    #     change users - form\n{form_element}''')
    assert form_element.find('input', id='id_is_superuser')['checked'] is not None, (
        'Error, Superuser checkbox is not checked')
    # reload reg_user after being updated.
    reg_user = CustomUser.objects.get(id=reg_user.id)
    logger.debug('Initial user: %s', reg_user)
    assert reg_user.is_superuser is True
    # double check CustomUser.pre_save_call properly sets is_staff to true if is_superuser is true.
    assert reg_user.is_staff is True

    # --------------------------------------------------------------------
    logger.info('+++log in as user updated to superuser and confirm access to admin interface.')
    resp = client.post('/admin/login/?next=%2Fadmin%2F', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'username': REGUSER_EMAIL,
        'password': INITIAL_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, (
        'Error posting login form')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'''*****************************************************************************************
    #     listing users - soup:\n{soup}''')
    #
    # soup_screenshot(soup)
    # sys.exit(2)
    #
    assert soup.h1.get_text() == 'Site administration', (
        'Error, h1 header element does say this is the Site administration page')
    assert REGUSER_FNAME in soup.find(id='user-tools').get_text(), (
        'Error, we are not logged in as the initial user')

    """
    .. todo::

    - always set primary flag on email accounts, confirm it is set after creation of email
    - test user cannot log into site without email confirmation
    - test
    - test admin delete user and confirm soft deleted in listing.
    - test admin undelete regular user restores user fully
    - test admin hard delete of soft deleted user, and confirm no longer listed (or in database)
    - test admin change password process
    - test confirm user can login after change password.
    - +ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND = True
    - test admin Set password process

        .. code-block:: python

            # --------------------------------------------------------------------
            logger.debug('+++test admin Set password process.')
            resp = client.post('/admin/accounts/customuser/password/', {
                'email': 'superuserone@sample.org',
                'first_name': 'First',
                'last_name': 'Last',
                'superuser': 'on',
            }, follow=True)
            # confirm response is OK
            assert resp.status_code == 200, (
                'Error getting admin page')
            soup = BeautifulSoup(resp.content, 'html.parser')
            # confirm we are on the Add custom user page
            assert soup.find('h1').get_text() == 'Site administration', (
                'Error, we are not on the "Site administration" page')

    - Confirm regular user cannot log in to the admin interface
    - Test Admin sending email confirmation message for a user. see: test_custom_user_signup_client

    .. todo:: consider writing a utility function to get current url after redirect

    - after a redirect, url is not the same as requested, and it does not seem to be easily determined
    - it is not in the response headers, and there seems to be no url field
    - a `logger.debug(resp.redirect_chain)` produces: `[('/admin/accounts/customuser/2/change/', 302)]`
    - a `logger.debug(resp.redirect_chain[0][0])` produces: `/admin/accounts/customuser/2/change/`
    - function process:

        - confirm redirect chain is not empty (if not recdirected)
        - get length of list
        - if more than one entry, determine which is the current url
        - it seems that the first entry in the tuple is the url, and the second one is the redirect code.
    """

    """
    .. todo:: test to make sure we cannot log in to the regular site when soft deleted user

    .. todo:: confirm undeleted regular user can log in to the regular site

    .. todo:: put in password complexity safeguard tests.
    """


""".. todo:: test the email validation processes for the admin interface."""

""".. todo:: confirm reg_user can log into the admin interface with superuser flag set.

    .. code-block:: python

        # --------------------------------------------------------------------
        logger.debug('+++confirm reg_user can log into the admin interface with superuser flag set .')
        logout_form_element = soup.select_one('#container #header #user-tools #logout-form')
        assert logout_form_element.get('action') == '/admin/logout/', (
            'Error, logout form action is not /admin/logout/')
        assert logout_form_element.find('button', attrs={'type': 'submit'}).get_text() == 'Log out', (
            'Error, missing logout button')
"""


def save_custom_user_change_fields(form_element: bs4.element.Tag):
    """Save the custom user change fields from get(f'/admin/accounts/customuser/{reg_user.id}/change/')."""
    change_fields = {}
    change_fields['username'] = form_element.find('input', attrs={'name': 'username'}).get('value')
    change_fields['email'] = form_element.find('input', attrs={'name': 'email'}).get('value')
    change_fields['first_name'] = form_element.find('input', attrs={'name': 'first_name'}).get('value')
    change_fields['last_name'] = form_element.find('input', attrs={'name': 'last_name'}).get('value')
    is_active_readonly_field = form_element.select_one("div.field-is_active div.readonly img[alt='True']")
    change_fields['is_active'] = True if is_active_readonly_field is not None else False
    is_staff_readonly_field = form_element.select_one("div.field-is_staff div.readonly img[alt='True']")
    change_fields['is_staff'] = True if is_staff_readonly_field is not None else False
    """..todo :: consider coding to get is_superuser field in the admin site testing when using beautifulsoup as follows:
        - Note: BeautifulSoup does not get the final value of checkbox fields.  To do this without using Playwright or Selenium:
            1. Use the TESTING context processor so that we can output to the browser only when in testing mode.
                - see healthy_meals/context_processors.py - def testing_context
                - see: healthy_meals.settings.py - TEMPLATES "OPTIONS" "context_processors" references: "healthy_meals.context_processors.testing_context"
            2. Loop through the fields in the admin site fieldset to get the is_superuser field value
                - see templates/admin/accounts/custom_user/admin_change_testing_debugging.html
            3. Write the html to hidden field in the form.
                - see templates/admin/accounts/custom_user/admin_change_testing_hidden.html
            4. Test to confirm that all of these pieces work properly and together.
    """
    change_fields['last_login_time'] = form_element.find('input', id='id_last_login_1').get('value')
    change_fields['date_joined_date'] = form_element.find('input', id='id_date_joined_0').get('value')
    change_fields['date_joined_time'] = form_element.find('input', id='id_date_joined_1').get('value')
    return change_fields
