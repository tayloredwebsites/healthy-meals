import pytest
from django.test import Client

from django.contrib.admin.sites import AdminSite

from accounts.models import CustomUser
from accounts.admin import CustomUserAdmin

from bs4 import BeautifulSoup

import logging

from django.db import IntegrityError, transaction
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


#############################################################################
@pytest.mark.django_db
def test_custom_user_crud_admin(get_init_user):  # get_init_user):
    """Test admin site flow to test CustomUser CRUD (create, read/view, update, soft delete,  and list users.

    .. todo:: test the creation of regular users, who are then changed to superuser, and confirm they have access to the admin site
        - It seems that to create a test superuser who has access to the admin site must be created by CustomUser.objects.create_superuser()
        - does this mean that we will not be able to change existing test users to superuser?
        - is there an issue with this in development (or production)?

    .. todo:: set logging level for running nox testing session to error (don't show info messages normally)

    .. todo:: document maximum line length change from 120 to 200 to prevent pycharm formatting statements automatically
    """
    logger = logging.getLogger(__name__)

    logger.info(f'*** {__name__}::test_custom_user_create_admin - Starting')
    client = Client()
    sup_user = get_init_user

    assert CustomUser.objects.count() > 0, (
        'There should be at least one CustomUser instances')

    # --------------------------------------------------------------------
    logger.info('*** go to admin site, get and validate login page.')
    resp = client.get('/admin/', follow=True)
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting admin page')
    assert not resp.wsgi_request.user.is_authenticated, (
        'User should not be authenticated')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'soup: {soup}')
    assert soup.find(id='site-name').get_text() == 'Healthy Meals Admin', (
        'Error, we are missing the admin site title')
    form_element = soup.find(id='login-form')
    assert form_element['action'] == '/admin/login/?next=%2Fadmin%2F', (
        'Error, form should should have /admin/login/?next=%2Fadmin%2F for its action')
    assert form_element.find('input', id='id_username')['name'] == 'username', (
        'Error, we are missing the username input field')
    assert form_element.find('input', id='id_password')['name'] == 'password', (
        'Error, we are missing the password input field')

    # --------------------------------------------------------------------
    logger.info('*** post superuser login')
    resp = client.post('/admin/login/?next=%2Fadmin%2F', {
        # csrf_elem['name']: csrf_elem['value'],  # csrf token
        'username': INITIAL_USER_EMAIL,
        'password': INITIAL_USER_PASSWORD,
    }, follow=True)
    assert resp.status_code == 200, (
        'Error posting login form')

    # --------------------------------------------------------------------
    logger.info('*** confirm that user is authenticated after logging in')
    assert resp.wsgi_request.user.is_authenticated, (
        'User should be authenticated')

    # --------------------------------------------------------------------
    logger.info('*** get the "Healthy Meals Admin" page once logged in.')
    resp = client.get('/admin/', follow=True)
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting admin page')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'soup: {soup}')
    assert not 'are not authorized to access this page' in soup.find(id='content-main').get_text(), (
        'Error, we are unauthorized to access this page')

    # get the Accounts (CustomUser) section of the page
    accounts_div = soup.find('div', class_='app-accounts')
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
    logger.info('*** simulate a click on the "+ Add" link to GET the "Add custom user" page & its form.')
    resp = client.get('/admin/accounts/customuser/add/')
    # confirm response is OK
    assert resp.status_code == 200, (
        'Error getting admin page')
    soup = BeautifulSoup(resp.content, 'html.parser')
    # logger.debug(f'soup: {soup}')
    # confirm we are on the Add custom user page
    assert soup.find('h1').get_text() == 'Add custom user', (
        'Error, we are not on the "Add custom user" page')

    # --------------------------------------------------------------------
    logger.info('*** get and Validate the "Add custom user" form.')
    form_elem = soup.find(id='customuser_form')
    # logger.debug(f'form_elem: {form_elem}')
    assert form_elem.find('input', id='id_email')['name'] == 'email', (
        'Error, we are missing the email input field')
    assert form_elem.find('input', id='id_first_name')['name'] == 'first_name', (
        'Error, we are missing the first name input field')
    assert form_elem.find('input', id='id_last_name')['name'] == 'last_name', (
        'Error, we are missing the last name input field')
    assert form_elem.find('input', id='id_is_superuser')['name'] == 'is_superuser', (
        'Error, we are missing the is superuser input field')
    assert form_elem.find('input', id='id_is_superuser')['type'] == 'checkbox', (
        'Error, superuser input field is not a checkbox')
    assert 'No password set.' in form_elem.find('div', id='id_password').get_text(), (
        'Error, we are missing the no password set message.')
    assert form_elem.find('input', attrs={'type': 'submit', 'class': 'default'})['value'] == 'Save', (
        'Error, we are missing the default "SAVE" button')
    assert form_elem.find('input', attrs={'name': '_addanother'})['value'] == 'Save and add another', (
        'Error, we are missing the "Save and add another" button')
    assert form_elem.find('div', id='id_password').find('a', attrs={'class': 'button'})['href'] == '../password/', (
        'Error, we are missing the "Set password" button')
    assert form_elem.find('input', attrs={'name': '_continue'})['value'] == 'Save and continue editing', (
        'Error, we are missing the "Save and continue editing" button')

    # --------------------------------------------------------------------
    logger.info('*** create new superuser without setting password')
    # Add custom user" simulating clicking the form save button, returning integrity error from null password
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            resp = client.post('/admin/accounts/customuser/add/', {
                'email': 'superuserone@sample.org',
                'first_name': 'First',
                'last_name': 'Last',
                'superuser': 'on',
            })  # , follow=True)

    # --------------------------------------------------------------------
    logger.info('*** simulate clicking on the "Set password" button .')
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
    logger.debug(f'soup: {soup}')
    # confirm we are on the Add custom user page
    assert soup.find('h1').get_text() == 'Site administration', (
        'Error, we are not on the "Site administration" page')

    # --------------------------------------------------------------------
    logger.info('*** Confirm new superuser has access to admin site .')

    # --------------------------------------------------------------------
    logger.info('*** Create regular user with new superuser using all save options.')

    # --------------------------------------------------------------------
    logger.info('*** Confirm regular user cannot login to the admin site. .')

    # --------------------------------------------------------------------
    logger.info('*** Soft delete regular user with initial user')

    # --------------------------------------------------------------------
    logger.info('*** confirm we cannot login to the regular site when soft deleted new regular user.')

    # --------------------------------------------------------------------
    logger.info('*** undelete regular user with initial user')

    # --------------------------------------------------------------------
    logger.info('*** confirm undeleted regular user can login to the regular site.')

    # --------------------------------------------------------------------
    logger.info('*** change regular user and set to superuser, use all save buttons, confirm access to admin site.')

    # --------------------------------------------------------------------
    logger.info('***  set initial user password to invalid, then valid, then login.')

    # --------------------------------------------------------------------
    logger.info('*** Soft and Hard delete regular user with initial user, and confirm with database calls.')

    # --------------------------------------------------------------------
    logger.info('*** Change names of initial user.')

    # --------------------------------------------------------------------
    logger.info('***  change password of initial user, logout, and login.')

    # # --------------------------------------------------------------------
    # logger.info('***  .')
    #
    # # --------------------------------------------------------------------
    # logger.info('***  .')
    #
    # # --------------------------------------------------------------------
    # logger.info('***  .')
    #
    # # --------------------------------------------------------------------
    # logger.info('***  .')
    #
    # # --------------------------------------------------------------------
    # logger.info('***  .')
