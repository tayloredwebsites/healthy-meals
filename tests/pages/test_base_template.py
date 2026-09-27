import pytest
from accounts.models import CustomUser
from django.db import IntegrityError, transaction
from django.test import Client
from django.urls import reverse
from bs4 import BeautifulSoup
from tests.accounts.factories import CustomUserFactory
import logging
logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_base_not_logged_in():
    # get starting user record count
    logger.debug('Starting Starting test_base_template.py::test_base_not_logged_in')

    client = Client()
    # get home page for any user (logged in or not)
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200
    # Check the Header Font Sizers
    # parse the html response
    soup = BeautifulSoup(resp.content, 'html.parser')
    # confirm we are on the home page of this site
    assert soup.h1.get_text() == "Healthy Meals: Diet Assistant"
    assert soup.h2.get_text() == "Home"
    # confirm the 5 font sizers are in the header
    sizer_tags = soup.find(id='fontSizer').find_all('a')
    assert len(sizer_tags) == 5
    # Check the Header Nav bar
    # confirm the navigation bar has two items - (home and about)
    nav_tags = soup.find(id='topMenu').find_all('a')
    assert len(nav_tags) == 3  # 3 top navigation items
    nav_home_link_tag = soup.find(id='topMenu').find_all('a', href='/')
    assert len(nav_home_link_tag) == 1
    nav_about_link_tag = soup.find(id='topMenu').find_all('a', href='/about/')
    assert len(nav_about_link_tag) == 1

    # confirm not logged in at home page with displays for user as not logged in
    tsm = soup.find(id="topSysMenu")
    logger.debug(f'tm : {tsm}')
    tsm_ne = tsm.find(id="tsm_friend")
    logger.debug(f'tsm_ne: {tsm_ne}')
    assert "Friend" in tsm_ne
    # confirm the navigation bar has two items - (password change and logout)
    assert len(tsm.find('a', href='/accounts/login/')) == 1
    assert len(tsm.find('a', href='/accounts/signup/')) == 1

    #############################################
    # Check About page displays
    #############################################


@pytest.mark.django_db
def test_base_logged_in():
    """
    - Validate base template display
    - ensure user with name is displayed using their name
    - pytest tests/pages/test_base_template.py::test_base_logged_in
    """
    logger.debug('Starting test_base_template.py::test_base_logged_in')

    #############################################
    # Check Logged in displays properly
    #############################################
    client = Client()

    # create a user and log in to the test system
    user = CustomUserFactory.create(email='test@sample.com', password='password#123')
    # # attempt to login using using login functon - always returns false
    # user.set_password('password#123')
    # user.save
    # response = client.login(email='test@sample.com', password='password#123')
    # assert response == True

    # # unable to use standard login, must force_login
    client.force_login(user)

    # get home page for logged in user
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200
    # parse the html response
    soup = BeautifulSoup(resp.content, 'html.parser')
    # print('Logged in user web page:')
    # print(soup.prettify())

    # confirm logged in at home page with displays for user as logged in
    tsm = soup.find(id="topSysMenu")
    logger.debug(f'tm : {tsm}')
    tsm_ne = tsm.find(id="tsm_name_email")
    logger.debug(f'tsm_ne: {tsm_ne}')
    assert "{fname} {lname}".format(fname=user.first_name, lname=user.last_name) in tsm_ne
    # confirm the navigation bar has two items - (password change and logout)
    assert len(tsm.find('a', href='/accounts/password/change/')) == 1
    assert len(tsm.find('a', href='/accounts/logout/')) == 1


@pytest.mark.django_db
def test_no_name_has_email():
    """
    - ensure user without a name is displayed using their email
    - pytest tests/pages/test_base_template.py::test_no_name_has_email
    """
    logger.debug('Starting test_no_name_has_email')
    client = Client()  # get web client

    # create a user and log in to the test system
    user = CustomUserFactory.create(email='test@sample.com', password='password#123', first_name='', last_name='')
    # # unable to use standard login, must force_login
    client.force_login(user)

    # get home page for logged in user
    resp = client.get(reverse("home"))
    # confirm response is OK
    assert resp.status_code == 200
    # parse the html response
    soup = BeautifulSoup(resp.content, 'html.parser')
    logger.debug('Logged in user web page:')
    logger.debug(soup.prettify())

    # confirm logged in at home page with displays for user as logged in
    tsm = soup.find(id="topSysMenu")
    logger.debug(f'tm : {tsm}')
    tsm_ne = tsm.find(id="tsm_name_email")
    logger.debug(f'tsm_ne: {tsm_ne}')
    assert user.first_name == ''
    assert user.last_name == ''
    assert user.email != '' and user.email != None
    logger.debug(f'email: {user.email}')
    assert user.email in tsm_ne

#############################################
# Check Logged in page displays email if missing first or last name
#############################################

#############################################
# Check Logged in - change password process works correctly
#############################################

#############################################
# Check log out process works correctly
#############################################

#############################################
# Check password change process works correctly
#############################################

#############################################
# Check password reset process works correctly
#############################################

#############################################
# Check signup process works correctly
#############################################
