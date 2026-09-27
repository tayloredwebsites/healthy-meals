from django.test import TestCase
from unittest import skip
from django.urls import reverse
from bs4 import BeautifulSoup
from tests.accounts.factories import CustomUserFactory
import logging
logger = logging.getLogger(__name__)

#
@skip
class BaseLayoutTestCase(TestCase):
    """skipping this test. see tests.accounts.test_database_cases::UserModelsTestCase Issues"""
    def setUp(self):
        # Setup run before every test method.
        pass

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_base_layout_not_logged_in(self):
        # get home page for any user (logged in or not)
        resp = self.client.get(reverse("home"))
        # response is OK
        self.assertEqual(resp.status_code, 200)
        ### Check the Header Font Sizers
        # parse the html response
        soup = BeautifulSoup(resp.content, 'html.parser')
        ### confirm we are on the home page of this site
        self.assertEqual(soup.h1.get_text(), "Healthy Meals: Diet Assistant")
        self.assertEqual(soup.h2.get_text(), "Home")
        # confirm the 5 font sizers are in the header
        sizer_tags = soup.find(id='fontSizer').find_all('a')
        self.assertEqual(len(sizer_tags), 5)
        ### Check the Header Nav bar
        # confirm the navigation bar has two items - (home and about)
        nav_tags = soup.find(id='topMenu').find_all('a')
        self.assertEqual(len(nav_tags), 3) # 3 top navigation items
        nav_home_link_tag = soup.find(id='topMenu').find_all('a', href='/')
        self.assertEqual(len(nav_home_link_tag), 1)
        nav_about_link_tag = soup.find(id='topMenu').find_all('a', href='/about/')
        self.assertEqual(len(nav_about_link_tag), 1)

         ### Check the Header Nav bar (when not logged in)
        # confirm the navigation bar has two items - (home and about)
        nav_tags = soup.find(id='topSysMenu').find_all('a')
        self.assertEqual(len(nav_tags), 2)
        login_link_tag = soup.find(id='topSysMenu').find_all('a', href='/accounts/login/')
        self.assertEqual(len(login_link_tag), 1)
        signup_link_tag = soup.find(id='topSysMenu').find_all('a', href='/accounts/signup/')
        self.assertEqual(len(signup_link_tag), 1)

    def test_base_logged_in(self):
        # create a user and "force" it to be logged in to the test system
        user = CustomUserFactory.create(email='test@sample.com', password='password#123')
        self.client.force_login(user)
        # get home page
        resp = self.client.get(reverse("home"))
        # response is OK
        self.assertEqual(resp.status_code, 200)
        # parse the html response
        soup = BeautifulSoup(resp.content, 'html.parser')
         ### Check the Header Nav bar (when logged in)
        # confirm the navigation bar has two items - (password change and logout)
        nav_tags = soup.find(id='topSysMenu').find_all('a')
        self.assertEqual(len(nav_tags), 2)
        logger.debug(nav_tags)
        pwd_change_link_tag = soup.find(id='topSysMenu').find_all('a', href='/accounts/password/change/')
        self.assertEqual(len(pwd_change_link_tag), 1)
        logout_link_tag = soup.find(id='topSysMenu').find_all('a', href='/accounts/logout/')
        self.assertEqual(len(logout_link_tag), 1)
