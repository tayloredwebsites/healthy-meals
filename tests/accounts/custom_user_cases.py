# from django.test import TestCase
from django.test import TransactionTestCase
from .factories import CustomUserFactory

from accounts.models import CustomUser

from django.db import IntegrityError, transaction
from django.utils import timezone

import pytest # to run pytest fixture using usefixtures

# https://pytest.org/en/latest/how-to/fixtures.html#request-context
# https://pytest.org/en/latest/how-to/unittest.html

# @pytest.mark.usefixtures('get_case_superuser1', 'db_client', 'client', 'admin_client')
# @pytest.mark.usefixtures('admin_client', 'django_db_reset_sequences') # reset sequences doesn't work here
@pytest.mark.usefixtures('get_case_superuser1', 'django_db_reset_sequences', 'db')
@pytest.mark.skip(reason="Should TestCase tests be supported? Keep this.")
class UserModelsTestCase(TransactionTestCase):
    """using testcase with factoryboy for testing updates to the database.

    Issues::

        - skipping this test, as running the "get_case_superuser1" fixture is not being run before every test!
            - I suspect that the complexities of integrating TestCase with pytest fixtures are not completely resolved.
            - I will not spend any more time on maintaining TestCase automated tests (that are meant to be run under pytest).
        - Used pytest fixtures using TestCase per: https://pytest.org/en/4.6.x/unittest.html
            - Got "reset_sequences" to work using "TransactionTestCase" with a "reset_sequences = True" statement.  Notes:
                - Was unable to pass the "reset_sequences" parameters to "db_client" wihin the "usefixtures()" mark
                - Then was able to track down a way to reset sequences when using TestCase under pytest.  See:
                    - saw this on stackoverflow @ https://stackoverflow.com/questions/51504144/how-can-i-reset-a-django-test-database-ids-after-each-test?atabase-ids-after-each-test#answer-67576020
                    - in the django_db mark reset_sequences docs @ https://pytest-django.readthedocs.io/en/stable/helpers.html#pytest.mark.django_db
                        - there is a statement: "For details see django.test.TransactionTestCase.reset_sequences":
                            - https://docs.djangoproject.com/en/stable/topics/testing/advanced/#django.test.TransactionTestCase.reset_sequences
                        - which can be found in the "Advanced testing topics" page, under "Advanced features of TransactionTestCase":
                            - https://docs.djangoproject.com/en/6.0/topics/testing/advanced/#advanced-features-of-transactiontestcase
            - Got error signing in of user in fixture:
                - Tried adding "admin_client" to "usefixtures()" since it automatically creates a superuser with a username of admin, and an email of admin@example.com
                    - https://pytest-django.readthedocs.io/en/latest/helpers.html#admin-client-django-test-client-logged-in-as-admin
                    - https://pytest-django.readthedocs.io/en/latest/helpers.html#admin-user-an-admin-user-superuser
                    - however, the reset_sequences was ignored, and did not return a user with an ID of 1
                - attempted login of user using the pytest fixture "client" for pytest fixture "conftest::get_case_superuser1()", got errors:
                    - error: ScopeMismatch: You tried to access the function scoped fixture client with a class scoped request object. Requesting fixture stack:
                - Then did sign in of user in the standard "TestCase" "setUp()" method.
            - removed setUp(), and tearDown() due to problems with pytext fixtures running with class scope:
                - with class scope, the fixtures are only run once for the class, and not for each test
                - we need the user's reset between each test, because they run independently from each other.
    """

    reset_sequences = True

    @pytest.mark.skip(reason="Should TestCase be supported? Is code to confirm user with ID 1 is a superuser?  Delete this?")
    def test_reset_sequences(self):
        '''Test to ensure database record ID values are reset for each test using "django_db" "reset_sequences".
        
        See "Notes" under "UserModelsTestCase" for how to get "reset_sequences" to work with "TestCase" under "pytest".
        '''

        print(f'*** {__name__}::test_reset_sequences - confirm get_case_superuser1() has run')
        assert hasattr(self, "user_info"), 'Missing the self.user_info from get_case_superuser1()'

        print(f'*** {__name__}::test_reset_sequences - Sign in self.signed_in_user')
        self.signed_in_user = self.user_info['user']
        self.client.login(email=self.user_info['email'], password=self.user_info['password'])

        print(f'*** {__name__}::test_reset_sequences - Get user from "get_case_superuser1()" fixture and "setUp()".')
        signed_in_user = self.signed_in_user

        # # test debugging code
        # print(f'signed_in_user: {signed_in_user}')
        # print(f'{signed_in_user:detail}')

        print(f'*** {__name__}::test_reset_sequences - confirm we have a new logged in superuser')
        assert signed_in_user.id == 1, 'ID reset is not working, ID is not 1 (see "Notes" under "UserModelsTestCase")'
        assert signed_in_user.is_superuser, 'signed_in_user was not set up as superuser'
        assert signed_in_user.is_authenticated, 'signed_in_user is not logged in'



    @pytest.mark.skip(reason="Should TestCase be supported? What is this testing, and is it needed?  Delete this?")
    def base_user_case(self):
        '''TestCase version of tests.accounts.test_database::test_custom_user
        
        For docs, see:

            - tests.accounts.test_database.UserModelsTestCase
            - tests.accounts.test_database_cases.test_custom_user
        '''

        print(f'*** {__name__}::test_reset_sequences - confirm get_case_superuser1() has run')
        assert hasattr(self, "user_info"), 'Missing the self.user_info from get_case_superuser1()'

        print(f'*** {__name__}::test_reset_sequences - Sign in self.signed_in_user')
        self.signed_in_user = self.user_info['user']
        self.client.login(email=self.user_info['email'], password=self.user_info['password'])

        print(f'*** {__name__}::test_reset_sequences - Get user from "get_case_superuser1()" fixture and "setUp()".')
        signed_in_user = self.signed_in_user

        # # admin_client fixture fails this
        # assert CustomUser.objects.count() == 1, 'fixture did not flush and add superuser to database'
        # # signed_in_user = CustomUser.objects.get(id=1)
        # signed_in_user = CustomUser.objects.first()
        # assert signed_in_user.id == 1, 'signed in user does not have an id of 1'

        # test debugging code
        # print out all users
        for rec in CustomUser.objects.all():
            print(f'*** {__name__}::test_custom_user - user: {rec}')
            # print(f'*** {__name__}::test_custom_user - user: {rec:detail}')

        print(f'*** {__name__}::test_case_custom_user - confirm we have a new logged in superuser')
        assert signed_in_user.id == 1, 'ID reset is not working, ID is not 1 (see notes)'
        assert signed_in_user.is_superuser, 'signed_in_user was not set up as superuser'
        assert signed_in_user.is_authenticated, 'signed_in_user is not logged in'

        print('*** {__name__}::test_case_custom_user - Initial Setup')
        start_time = timezone.now() # get current time at start of test
        initial_count = CustomUser.objects.count()
        assert CustomUser.objects.count() == 1, 'the signed_in_user is not the only user at the start of test'

        print('*** {__name__}::test_case_custom_user - create 4 test users')
        test_users = CustomUserFactory.create_batch(4,
            created_by=signed_in_user, # manually put in the creating user
            updated_by=signed_in_user, # manually put in the creating user
        )


        print('*** {__name__}::test_case_custom_user - confirm we have 4 more users')
        assert initial_count + 4 == CustomUser.objects.count(), 'Invalid record count - # of users is not initial signed in user plus 4'

        user0 = test_users[0] # save first added user to variable

        print(f'*** {__name__}::test_case_custom_user - validate the created_at, updated_at, created_by, and updated_by fields')
        assert (user0.created_at - start_time).total_seconds() < 1.0, 'user0 created_at time is too long ago'
        assert (user0.updated_at - start_time).total_seconds() < 1.0, 'user0 updated_at time is too long ago'
        assert user0.created_by == signed_in_user, 'user0 created_by is not creating user (signed_in_user)'
        assert user0.updated_by == signed_in_user, 'user0 updated_by is not creating user (signed_in_user)'

        print(f'*** {__name__}::test_case_custom_user - validate user0 soft deletes & history (audit trail)')
        assert user0.rec_history_count() == 1, 'user0 history is not starting out with 1 record'
        assert not user0.rec_history_field_changed(0, 'deleted'), 'user0 history has user0 as deleted'

        print(f'*** {__name__}::test_case_custom_user - Soft Delete of user0')
        user0.delete()
    
        # # test debugging code
        # # print out history records
        # for n in range(hist_recs_count):
        #     print(f'*** {__name__}::test_case_custom_user - user0 after deleted history [{n}]: {user0.history.all()[0].changes_dict}')
        # # print out all users and show their deleted status
        # for rec in CustomUser.objects.all_with_deleted():
        #     print(f'*** {__name__}::test_case_custom_user - After soft delete record 0: {rec.email}: {rec.username}, {rec.deleted}')

        print(f'*** {__name__}::test_case_custom_user - Soft Deleted of user: {user0.email}: {user0.username}, {user0.deleted}')
        assert user0.deleted, 'soft delete of user0  was not successful'
        assert user0.rec_history_count() == 2, 'user0 history does not have 2 records, with the new deleted record'

        assert user0.rec_history_field_changed(0, 'deleted'), 'history was not changed to say it is currently deleted'
        assert user0.rec_history_field_was(0, 'deleted') == 'None', 'history does not say it was previously not deleted'
        assert user0.rec_history_field_is_now(0, 'deleted') == user0.deleted.strftime("%Y-%m-%d %H:%M:%S.%f"), 'history time of deletion does not match record time of deletion'
        assert CustomUser.objects.all_with_deleted().count() == initial_count + 4, 'all users including soft deleted ones should still be initial signed in user plus 4'
        assert CustomUser.objects.deleted_only().count() == 1, 'soft deleted user count should now be 1'

        print(f'*** {__name__}::test_case_custom_user - ensure the database does not allow duplicate users (with the same email), even if soft deleted')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                CustomUserFactory(
                    email=user0.email,
                    username=user0.username,
                    first_name=user0.first_name,
                    last_name=user0.last_name,
                )

        # # test debugging code
        # for rec in CustomUser.objects.all_with_deleted():
        #     print(f'After factory attempt to create duplicate of record 0: {rec.email}: {rec.username}, {rec.deleted}')

        print(f'*** {__name__}::test_case_custom_user - validate deleted user is reflected properly in CustomUser methods')
        assert CustomUser.objects.all().count() == 4
        assert CustomUser.objects.all_with_deleted().count() == 5
        assert CustomUser.objects.deleted_only().count() == 1

        print(f'*** {__name__}::test_case_custom_user - undelete the soft deleted user')
        test_users[0].undelete()

        print(f'*** {__name__}::test_case_custom_user - confirm user undelete is reflected properly in CustomUser methods')
        assert CustomUser.objects.all().count() == 5
        assert CustomUser.objects.all_with_deleted().count() == 5
        assert CustomUser.objects.deleted_only().count() == 0

