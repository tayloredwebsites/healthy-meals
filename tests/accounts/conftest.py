# tests (accounts) conftest.py

"""accounts conftest.py file for configuration of CustomUser tests

    Notes::

    .. todo::
        - review need for get_superuser_info(), get_logged_in_superuser(), and get_case_superuser1() fixtures
        - clean up unneeded commented out code.

"""
import pytest
from pprint import pprint
from typing import List, Optional, Tuple, Any, Generator
from django.db import connection

import pytest
from accounts.models import EmailAddress
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

# from decouple import config
from accounts.models import CustomUser

from unittest.mock import patch, Mock, AsyncMock, MagicMock

from allauth.account.auth_backends import AuthenticationBackend

from tests.accounts.factories import CustomUserFactory

from typing import List, Optional, Tuple, Any, Generator

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

""".. todo:: put testing constants into fixture"""


########################################################################################################################
# PYTEST FIXTURES

# @pytest.mark.django_db # PytestRemovedIn9Warning: Marks applied to fixtures have no effect
#   See docs: https://docs.pytest.org/en/stable/deprecations.html#applying-a-mark-to-a-fixture-function
@pytest.fixture
def get_init_user():
    # sup_user = CustomUserFactory.create(
    #     email=INITIAL_USER_EMAIL,
    #     username='superuser',  # should be changed to email upon save!
    #     password=INITIAL_USER_PASSWORD,
    #     first_name='Super',
    #     last_name='User',
    #     is_superuser=True,
    # )
    sup_user = CustomUser.objects.create_superuser(
        email=INITIAL_USER_EMAIL,
        username='superuser',  # should be changed to email upon save!
        password=INITIAL_USER_PASSWORD,
        first_name='Super',
        last_name='User',
        is_superuser=True,
    )
    assert CustomUser.objects.count() == 1, 'the signed_in_user is not the only user at the start of test'
    yield sup_user


# @pytest.mark.django_db
# def is_user_valid(email: str) -> bool:
#     user = get_or_create_custom_user(email= email)

# @pytest.mark.django_db
# @patch('django.contrib.auth.authenticate')
# @patch('django.contrib.auth.login')
# def test_successful_login(mock_login, mock_authenticate, client):
#     # Create a user with a special password
#     user = User.objects.create_user(
#         username='testuser',
#         email='test@example.com',
#         password='specialpassword123'
#     )
#
#     # Mock the authenticate method to return the user when called with the special password
#     mock_authenticate.return_value = user
#
# @pytest.fixture
# def mock_allauth_authenticate() -> Generator[MagicMock | AsyncMock, Any, None]:
#     with patch('allauth.account.auth_backends.AuthenticationBackend.authenticate') as mock:
#         yield mock
#
# @pytest.fixture
# def mock_django_authenticate(mocker) -> Generator[MagicMock | AsyncMock, Any, None]:
#     with patch('django.contrib.auth.authenticate') as mock:
#         yield mock

########################################################################################################################
# TESTING UTILITY METHODS

def is_user_valid(user: CustomUser) -> dict[str, bool | List[str]]:
    errs: List[str] = []
    # return_dict: dict[str, bool | List[str]] = {}
    print(f'*** {__name__} - is_user_valid - user: {user: detail}')
    # validate the user
    try:
        user.full_clean()
        print('user is validated')
        return {'valid': True, 'errors': []}
    except ValidationError as ex:
        errs.extend(get_invalid_fields(ex))
        return {'valid': False, 'errors': errs}


def get_invalid_fields(exception: ValidationError) -> list[str]:
    errs: List[str] = []
    for field, errors in exception:
        print(f'{field}: {errors}')
        for err in errors:
            print(f'{err}')
            errs.append(f'{err} (in {field})')
    pprint(errs)
    return errs


def is_user_email_validated(user: CustomUser) -> Tuple[bool, str]:
    """Has the email record for this CustomUser been validated?

    Returns:: a tuple: (
            is_valid: bool, # True, or False
            err_str: str, # returns '' if no errors
        )
    """
    try:
        print(f'*** {__name__} - is_user_email_validated: for {user.email}?')
        email_obj: EmailAddress = EmailAddress.objects.get_for_user(user, user.email)
        print(f'*** email address: {user.email} has email_obj: {email_obj:detail}, with verified: {email_obj.verified}')
        return (
            email_obj.verified,
            '',
        )
    except CustomUser.DoesNotExist:
        print(f'*** CustomUser for email: {user.email} does not exist')
        return (
            False,
            f'EmailAddress record for for email: {user.email} does not exist',
        )
    except Exception as ex:
        print(f'exception: {ex}')
        return (
            False,
            f'exception {ex} getting EmailAddress record for for email: {user.email}',
        )


def validate_user_email(email: str) -> Tuple[Optional[CustomUser], Optional[EmailAddress]]:
    try:
        print(f'*** {__name__} - validate_user_email - check if user for email: {email} exists')
        user: CustomUser = CustomUser.objects.get(email=email)
        print(f'*** found user: {user: detail} for email: {email}')
        # print(f'*** count of CustomEmailAddress records: {len(CustomEmailAddress.objects.all())}')
        # email_obj: CustomEmailAddress = CustomEmailAddress.objects.get_for_user(user, email)
        print(f'*** count of EmailAddress records: {len(EmailAddress.objects.all())}')
        email_obj: EmailAddress = EmailAddress.objects.get_for_user(user, email)
        print(f'*** email address: {email} has email_obj: {email_obj:detail}')
        email_obj.verified = True
        email_obj.save()
        return user, email_obj
    except CustomUser.DoesNotExist:
        print(f'*** CustomUser for email: {email} does not exist')
        return None, None
    except Exception as ex:
        print(f'exception: {ex}')
        return None, None


def get_or_create_custom_user(**kwargs):
    """Create CustomUser by matching email address, or creating a new one

    Notes::

        - to get an existing user, pass email only (args section)
        - do a return section
        - This is needed because factoryboy does not create related EmailAddress record
            - to be able to validate a CustomUser, it needs the attached EmailAddress
        - This method will not confirm the email address
            - see allauth.account.utils.create_user
            - see allauth.account.utils.complete_signup
        - Returns the new user, the info used to create it, and any errors.
    """
    # user = CustomUser.objects.get(email=email)
    errors: List[str] = []
    user: Optional[CustomUser] = None
    ret_dict: dict[str, CustomUser | None | dict] = {}

    print(f'*** {__name__} - get_or_create_custom_user - started')
    # print(f'*** {__name__} - get_or_create_custom_user - kwargs: {kwargs}')
    valid_field_names = ['id', 'email', 'first_name', 'last_name', 'password', 'is_superuser', 'is_staff', 'is_active']
    user_dict = {k: kwargs[k] for k in valid_field_names if k in kwargs}
    # pprint(f'*** {__name__} - get_or_create_custom_user user_dict:')
    # pprint(user_dict)
    if user_dict.get('user'):
        # we passed a user record.
        user = user_dict['user']
        #### validate the user, refactoring the validation below
        is_val, errs = is_user_valid(user)
        errors.append(errs)
        if not is_val:
            errors.append(f'User is not valid')
    elif user_dict['email']:
        # we passed the email, which is required if not passing a user.
        # make sure that we set the username to the email if we are creating it
        user_dict['username'] = user_dict['email']
        # load up the user info for return
        try:
            # first, try to find the user, and if so we are done
            user = CustomUser.objects.get(email=user_dict['email'])
            print('user exists')
        except CustomUser.DoesNotExist:
            # we did not find the user
            if len(user_dict) == 1:
                # we found the user, since we only passed the email, we are done
                pass
            else:
                print('load up the values for the user to be validated and created:')
                user = CustomUser(**user_dict)
                print(f'{user: detail}')
                is_val, errs = is_user_valid(user)
                errors.append(errs)
                if not is_val:
                    errors.append('User is not valid')
                else:
                    # call the allauth-django's special set_password function
                    if user_dict.get('password'):
                        user.set_password(user_dict['password'])
                    else:
                        errors.append(f'no password provided')
                    print('user is valid')
                    # user.save()
                    # # probably useless code because user is already validated
                    # try to create the user
                    try:
                        user.save()
                        print(f'saved user: {user: detail}')
                        EmailAddress.objects.create(user=user, email=user_dict['email'])  # verified=True, primary=True)
                    except Exception as ex:  # pragma: no cover
                        # We should not ever get here because we already validated 'user'
                        ex_name = ex.__class__.__name__
                        print(f'*** {__name__} - get_or_create_custom_user - save Exception: {ex_name} {ex}')
                        if ex_name == 'ValidationError':
                            errors.extend(get_invalid_fields(ex))
                        else:
                            raise ex
    else:
        errors.append('Missing required email field')
    # return {'user_dict': user_dict, 'errors': errors, 'user': user}
    return (user_dict, errors, user)


def get_url_from_email_body(body: str) -> str:
    msg_iter = iter(body.splitlines())
    for line in msg_iter:
        # print(line)
        if 'http://testserver' in line:
            rest_of_line = line.split('http://testserver', 1)[1]
            # print(f'*** rest_of_line: {rest_of_line}')
            return rest_of_line
    raise Exception('Error: No confirm email url found in body')

# # ----------------------------------------------------------------------------------------------------------------------
# # probably useless fixture to return a superuser preferably with an ID of 1
#
# @pytest.fixture()
# def get_custom_user(db, client): # django_db): #
#     """Pytest fixture for getting a custom_user as well as the info needed to be able to log it in.
#
#     # Notes:
#     #     - https://github.com/pytest-dev/pytest-randomly is used to ensure order of runs does not interfere with superuser with ID of 1 creation.
#     #
#     # Example:
#     #
#     # .. code-block:: python
#     #
#     #     # optionally test to make sure the ID reset works - need only include this once in testing
#     #     @pytest.mark.parametrize('rerun_of_test', [1, 2]) # optionally do a rerun of this test to confirm that the id is reset on each test
#     #
#     #     # example test to create superuser with ID of 1 with the info needed to be able to log it in.
#     #     @pytest.mark.django_db(transaction=True, reset_sequences=True)
#     #     def test_reset_sequences(get_superuser1_info):
#     #         ...
#     #         sup_user1_info = get_superuser1_info # call the fixture and return the info
#     #         sup_user1 = sup_user1_info['user'] # create the superuser
#     #
#     #         # optional tests, need only include this once in testing
#     #         assert sup_user1.id == 1, 'ID reset is not working, ID is not 1'
#     #         assert sup_user1.is_superuser, 'sup_user1 was not set up as superuser'
#     #         assert not sup_user1.is_authenticated, 'sup_user1 is logged in from get_superuser1_info fixture'
#     #
#     #         # log in sup_user1
#     #         client.login(email=sup_user1_info['email'], password=sup_user1_info['password'])
#     #         assert sup_user1.is_authenticated, 'sup_user1 did not get logged in'
#     #
#     #         # rest of test using superuser with ID of 1, who is not logged in yet.
#     # """
#     # return the super along with the info needed to login
#     return get_or_create_custom_user()
#
# #
# # # ----------------------------------------------------------------------------------------------------------------------
# # # probably useless fixture to return a superuser preferably with an ID of 1
# #
# # @pytest.fixture()
# # def get_logged_in_superuser(db, client):
# #     # """Pytest fixture for getting logged in superuser with ID of 1.
# #     #
# #     # Notes:
# #     #     - See get_superuser1_info() above
# #     #     - This is similar to the get_superuser1_info fixture, except:
# #     #         - the superuser is also logged in
# #     #         - the superuser is directly returned, without the login info
# #     #
# #     # Example:
# #     # .. code-block:: python
# #     #
# #     #     # example test to return a superuser with ID of 1 directly, who is logged in already.
# #     #     @pytest.mark.django_db(transaction=True, reset_sequences=True)
# #     #     def test_superuser1(get_logged_in_superuser1):
# #     #         ...
# #     #         sup_user1 = get_logged_in_superuser1 # call the fixture and return the superuser
# #     #
# #     #         # optional tests, need only include this once in testing
# #     #         assert sup_user1.id == 1, 'ID reset is not working, ID is not 1'
# #     #         assert sup_user1.is_superuser, 'sup_user1 was not set up as superuser'
# #     #         assert sup_user1.is_authenticated, 'sup_user1 did not get logged in'
# #     #
# #     #         # rest of test using superuser with ID of 1, who is not logged in yet.
# #     # """
# #     # able to sign in user as client exists here.
# #     sup_info = get_or_create_superuser()
# #     client.login(email=sup_info['email'], password=sup_info['password'])
# #     return sup_info['user']
# #
# # # ----------------------------------------------------------------------------------------------------------------------
# # # probably useless fixture to return a superuser preferably with an ID of 1
# #
# # @pytest.fixture(scope='class')
# # def get_case_superuser1(request):
# #     """See "Issues" under "tests.accounts.test_database_cases::UserModelsTestCase" for issues that finally got the TestCase tests skipped". """
# #     print(f'*** {__name__} - started')
# #     assert CustomUser.objects.count() == 0, 'Initial number of users is not 0'
# #     user_info = get_or_create_superuser()
# #     print(f'*** {__name__} - after add_or_create - CustomUser.objects.count(): {CustomUser.objects.count()}')
# #     print(f'*** {__name__} - user: {user_info['user']:detail}')
# #     request.cls.user_info = user_info
# #     print(f'*** conftest::get_case_superuser1() at return - CustomUser.objects.count(): {CustomUser.objects.count()}')
# #     return
#
#
# # # ----------------------------------------------------------------------------------------------------------------------
# # # probably useless fixture to return a superuser preferably with an ID of 1
# #
# # def get_or_create_superuser():
# #     """ add or create superuser with ID 1 & return user_info dict
# #
# #     When fixture is called, it will:
# #         - find the superuser with an ID of 1, or else create a new superuser.
# #             -  note: this is required because accounts.CustomUser has created_by, and updated_by fields that default to ID 1 of the site superuser
# #
# #     Notes:
# #         - https://pytest.org/en/latest/how-to/fixtures.html#request-context
# #         - https://pytest.org/en/latest/how-to/unittest.html
# #         - does this extend the pytext client?
# #         - does this reset the id values see django_db reset_sequences
# #             - thus superuser id may not be set to 1 in tests always
# #
# #     Args:
# #         - request: the [pytest requesting test context](https://pytest.org/en/latest/how-to/fixtures.html#request-context)
# #             - request.cls: the testing test context class (UnitTest Class calling this)
# #
# #     Returns:
# #         - the user_info dict, which includes:
# #             - the superuser at id = 1, or a newly created superuser @ id = 1
# #             - the username, email, and password, to be able to log in the user
# #     """
# #     print(f'*** {__name__} - started')
# #     user_info = {
# #         'username': USERNAME,
# #         'email': EMAIL,
# #         'password': PASSWORD,
# #     }
# #     initial_count = CustomUser.objects.count()
# #     if initial_count > 0:
# #         sup = CustomUser.objects.get(email=user_info['email'])
# #         assert sup.is_superuser, "CustomUser with email of {EMAIL} is not a superuser!"
# #         print(f'*** {__name__} - found first superuser: {sup:detail}')
# #         user_info['user'] = sup
# #         user_info['id'] = sup.id
# #     else:
# #         sup = CustomUser.objects.create(
# #             username=USERNAME,
# #             email=EMAIL,
# #             password=PASSWORD,
# #             is_superuser=True,
# #         )
# #         # # cannot create user with created_by, or updated_by to self, as self does not exist in the database yet.
# #         # sup.created_by = sup
# #         # sup.updated_by = sup
# #         sup.save()
# #         print(f'*** {__name__} - save() got CustomUser.objects.count(): {CustomUser.objects.count()}')
# #         print(f'*** {__name__} - Createdfirst superuser: {sup:detail}')
# #
# #         user_info['user'] = sup
# #         user_info['id'] = sup.id
# #     return user_info
# #
