
import pytest

from .factories import CustomUserFactory

from accounts.models import CustomUser

from django.db import IntegrityError, transaction

import logging
logger = logging.getLogger(__name__)

@pytest.mark.django_db
def test_user_soft_delete(setUpAndDown):
    '''Ensure soft deletes and undeletes update the database properly

        - emails are ensured to be unique,
        - CustomUser prints out as expected,
        - all_deleted (custom function) return the deleted custom users
        - run as large test to minimize database setup and teardown

        .. ToDo::
            test_database.py:
                - update to match test_database_cases.py updates:
                    - do setup as done in test_database_cases
                    - split out duplicate email tests from soft delete tests 

    '''
    # get starting 4 users and record count from init
    test_users = setUpAndDown
    assert CustomUser.objects.count() == 4
    test_users = CustomUser.objects.all()
    user0 = test_users[0]

    # confirm we have all 4 users, and show that none are soft deleted
    assert CustomUser.objects.all().count() == 4
    assert CustomUser.objects.all_with_deleted().count() == 4
    assert CustomUser.objects.all_deleted().count() == 0

    # confirm CustomUser history is as expected
    print(f'user0 history count: {user0.rec_history_count()}')
    assert user0.rec_history_count() == 1
    assert not user0.rec_history_field_changed(0, 'deleted')
    # ensure print output of CustomUser is correct
    assert user0.__str__() == f'{user0.email} - {user0.last_name}, {user0.first_name}'
    print(f'As Created: {user0.email}: {user0.username}, {user0.deleted}')

    # soft delete the first user
    user0.delete()
    print(f'Soft Deleted: {user0.email}: {user0.username}, {user0.deleted}')

    # confirm it was soft deleted
    assert CustomUser.objects.all().count() == 3
    assert CustomUser.objects.all_with_deleted().count() == 4
    assert CustomUser.objects.all_deleted().count() == 1

    # confirm CustomUser history is as expected
    hist_recs_count = user0.rec_history_count()
    print(f'user0 after deleted history count: {hist_recs_count}')
    for n in range(hist_recs_count):
        print(f'user0 after deleted history [{n}]: {user0.history.all()[0].changes_dict}')
    for rec in CustomUser.objects.all_with_deleted():
        print(f'After soft delete record 0: {rec.email}: {rec.username}, {rec.deleted}')
    assert user0.rec_history_count() == 2
    assert user0.rec_history_field_changed(0, 'deleted') # record 0 is the latest
    assert user0.rec_history_field_was(0, 'deleted') == 'None'
    assert user0.rec_history_field_is_now(0, 'deleted') == user0.deleted.strftime("%Y-%m-%d %H:%M:%S.%f")

    # # make sure the database does not allow duplicate emails for custom_users
    # # tests the pre_save signal that copies the email into the username field
    # # - this ensures that duplicate emails are not allowed at the database level
    # with pytest.raises(IntegrityError):
    #     with transaction.atomic():
    #         CustomUserFactory(
    #             email=test_users[0].email,
    #             username=test_users[0].username,
    #             first_name=test_users[0].first_name,
    #             last_name=test_users[0].last_name,
    #         )
    # for rec in CustomUser.objects.all_with_deleted():
    #     print(f'After factory attempt to create duplicate of record 0: {rec.email}: {rec.username}, {rec.deleted}')
    # assert CustomUser.objects.all_with_deleted().count() == 4
    # assert CustomUser.objects.all_deleted().count() == 1

    # undelete the user
    user0.undelete()

    assert CustomUser.objects.all_with_deleted().count() == 4
    assert CustomUser.objects.all_deleted().count() == 0
    print(f'Restored: {test_users[0].email}: {test_users[0].username}, {test_users[0].deleted}')


@pytest.mark.django_db
def test_unique_emails(setUpAndDown):
    '''Make sure that emails are always unique.'''
    # get starting 4 users and record count from init
    test_users = setUpAndDown
    assert CustomUser.objects.count() == 4
    test_users = CustomUser.objects.all()

    # confirm adding a duplicate record generates an IntegrityError
    with pytest.raises(IntegrityError):
        '''tests the pre_save signal that copies the email into the username field

        - this ensures that duplicate emails are not allowed at the database level

        '''
        with transaction.atomic():
            CustomUserFactory(
                email=test_users[0].email,
                username=test_users[0].username,
                first_name=test_users[0].first_name,
                last_name=test_users[0].last_name,
            )


@pytest.mark.django_db
def test_setUpAndDown(setUpAndDown):
    '''Ensure database automatically clears the database after setUpAndDown'''
    test_users = setUpAndDown

    # get starting 4 users and record count from init
    count = CustomUser.objects.count()
    assert count == 4

    ############################################ pytest fixtures ######################################

@pytest.fixture
def setUpAndDown():

    logger.debug('set up using setUpAndDown of test_database.py')
    # setUpAndDown fixture available to generate and pass data to test methods.
    # confirm no users at the start
    assert CustomUser.objects.count() == 0
    # create 4 test users
    testUsers = CustomUserFactory.create_batch(4)
    # confirm we now have 4 more
    assert CustomUser.objects.count() == 4

    # yield to tests, passing data to them
    logger.debug('yield setUpAndDown of test_database.py')
    yield testUsers
    logger.debug('finished yield of setUpAndDown of test_database.py')

    logger.debug(' setUpAndDown of test_database.py is done')
