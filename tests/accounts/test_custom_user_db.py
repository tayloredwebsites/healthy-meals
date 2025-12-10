import pytest
from django.test import Client
from django.urls import reverse
from bs4 import BeautifulSoup

from accounts.models import CustomUser
from .factories import CustomUserFactory
# from common.utils.user_utils import get_or_create_superuser


from django.db import IntegrityError, transaction
from django.utils import timezone

########################################################################################################################
# CONSTANTS FOR TESTING

from tests.testing_constants import (
    INITIAL_USER_EMAIL,
    INITIAL_USER_PASSWORD,
)

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


@pytest.mark.django_db  # (transaction=True, reset_sequences=True)
# def test_custom_user(signed_in_superuser):
def test_custom_user_db():  # (get_logged_in_superuser1):
    """Tests to ensure coverage of CustomUser App (preferred pytest version)

           - validate the created_at, updated_at, created_by, and updated_by fields
           - validate user0 soft deletes & history (audit trail)
           - ensure the database does not allow duplicate users (with the same email), even if soft deleted
           - validate deleted user is reflected properly in CustomUser methods
           - confirm user undelete is reflected properly in CustomUser methods

        Notes::

            - this is run as a large test to minimize database setup and teardown

        .. Todo::

            - test to make sure that deleted users cannot log into the system
            - test to make sure that undeleted users can still log into the system and function properly
    """

    print(f'*** {__name__}::test_custom_user_db - starting')

    sup_user = CustomUserFactory.create(
        email=INITIAL_USER_EMAIL,
        username=INITIAL_USERNAME,  # should be changed to email upon save!
        password=INITIAL_USER_PASSWORD,
        first_name=INITIAL_USER_FNAME,
        last_name=INITIAL_USER_LNAME,
        is_superuser=True,
    )
    start_time = timezone.now()  # get current time at start of test
    initial_count = CustomUser.objects.count()
    assert CustomUser.objects.count() == 1, 'the signed_in_user is not the only user at the start of test'

    print(f'*** {__name__}::test_custom_user - create 4 test users')
    test_users = CustomUserFactory.create_batch(
        4,
        created_by=sup_user,  # manually put in the creating user
        updated_by=sup_user,  # manually put in the updating user
    )

    # # test debugging code
    # # print out all users
    # for rec in CustomUser.objects.all():
    #     print(f'*** {__name__}::test_custom_user - user: {rec}')
    #     # print(f'*** {__name__}::test_custom_user - user: {rec:detail}')

    print(f'*** {__name__}::test_custom_user - confirm we have 4 more users')
    assert initial_count + 4 == CustomUser.objects.count(), 'Invalid record count - # of users is not initial signed in user plus 4'

    user0 = test_users[0]  # save first added user to variable

    print(f'*** {__name__}::test_custom_user - validate the created_at, updated_at, created_by, and updated_by fields')
    assert (user0.created_at - start_time).total_seconds() < 1.0, 'user0 created_at time is too long ago'
    assert (user0.updated_at - start_time).total_seconds() < 1.0, 'user0 updated_at time is too long ago'
    assert user0.created_by == sup_user, 'user0 created_by is not creating user (sup_user)'
    assert user0.updated_by == sup_user, 'user0 updated_by is not creating user (sup_user)'

    print(f'*** {__name__}::test_custom_user - validate user0 soft deletes & history (audit trail)')
    assert user0.rec_history_count() == 1, 'user0 history is not starting out with 1 record'
    assert not user0.rec_history_field_changed(0, 'deleted'), 'user0 history has user0 as deleted'

    print(f'*** {__name__}::test_custom_user - Soft Delete of user0')
    user0.delete()

    # # test debugging code
    # # print out history records
    # for n in range(hist_recs_count):
    #     print(f'*** {__name__}::test_custom_user - user0 after deleted history [{n}]: {user0.history.all()[0].changes_dict}')
    # # print out all users and show their deleted status
    # for rec in CustomUser.objects.all_with_deleted():
    #     print(f'*** {__name__}::test_custom_user - After soft delete record 0: {rec.email}: {rec.username}, {rec.deleted}')

    print(f'*** {__name__}::test_custom_user - Soft Deleted of user: {user0.email}: {user0.username}, {user0.deleted}')
    assert user0.deleted, 'soft delete of user0  was not successful'
    assert user0.rec_history_count() == 2, 'user0 history does not have 2 records, with the new deleted record'

    assert user0.rec_history_field_changed(0, 'deleted'), 'history was not changed to say it is currently deleted'
    assert user0.rec_history_field_was(0, 'deleted') == 'None', 'history does not say it was previously not deleted'
    assert user0.rec_history_field_is_now(0, 'deleted') == user0.deleted.strftime(
        "%Y-%m-%d %H:%M:%S.%f"), 'history time of deletion does not match record time of deletion'
    assert CustomUser.objects.all_with_deleted().count() == initial_count + 4, 'all users including soft deleted ones should still be initial signed in user plus 4'
    assert CustomUser.objects.deleted_only().count() == 1, 'soft deleted user count should now be 1'

    print(
        f'*** {__name__}::test_custom_user - ensure the database does not allow duplicate users (with the same email), even if soft deleted')
    with pytest.raises(IntegrityError):
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

    print(f'*** {__name__}::test_custom_user - validate deleted user is reflected properly in CustomUser methods')
    assert CustomUser.objects.all().count() == 4
    assert CustomUser.objects.all_with_deleted().count() == 5
    assert CustomUser.objects.deleted_only().count() == 1

    print(f'*** {__name__}::test_custom_user - undelete the soft deleted user')
    test_users[0].undelete()

    print(f'*** {__name__}::test_custom_user - confirm user undelete is reflected properly in CustomUser methods')
    assert CustomUser.objects.all().count() == 5
    assert CustomUser.objects.all_with_deleted().count() == 5
    assert CustomUser.objects.deleted_only().count() == 0
