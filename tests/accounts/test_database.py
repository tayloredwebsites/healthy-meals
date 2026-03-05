import pytest
import logging
logger = logging.getLogger(__name__)

from .factories import CustomUserFactory

from accounts.models import CustomUser

from django.db import IntegrityError, transaction

import datetime


@pytest.mark.django_db
def test_user_soft_delete():
    '''Ensure soft deletes and undeletes update the database properly

        - emails are ensured to be unique,
        - CustomUser prints out as expected,
        - deleted_only (custom function) return the deleted custom users
        - run as large test to minimize database setup and teardown
    '''
    # get starting user record count
    logger.debug('Starting TestUserModel::test_user_soft_delete')
    count = CustomUser.objects.count()
    # confirm no users
    assert count == 0
    start_time = datetime.datetime.now(datetime.UTC)
    # create 4 test users
    logger.debug(f'*** start_time: {start_time}')
    test_users = CustomUserFactory.create_batch(4)
    # confirm we now have 4 more
    assert count + 4 == CustomUser.objects.count()
    user0 = test_users[0]

    # validate the created and updated fields (should be within 1 second from start_time)
    logger.debug(f'*** user0 created time: {user0.created_at}')
    diff_created = user0.created_at - start_time
    logger.debug(f'*** diff_created: {diff_created}')
    assert diff_created.total_seconds() < 1.0
    diff_updated = user0.updated_at - start_time
    logger.debug(f'*** diff_updated: {diff_updated}')
    assert diff_updated.total_seconds() < 1.0

    logger.debug(f'*** user0 history count: {user0.rec_history_count()}')
    assert user0.rec_history_count() == 1
    assert not user0.rec_history_field_changed(0, 'deleted')
    # ensure print output of CustomUser is correct
    assert f'{user0.email}: {user0.last_name}, {user0.first_name}' in user0.__str__()
    logger.debug('As Created: %(email)s: %(username)s, %(deleted)s', {'email': user0.email, 'username': user0.username, 'deleted': user0.deleted})
    # soft delete the first user
    user0.delete()
    logger.debug('Soft Deleted: %(email)s: %(username)s, %(deleted)s', {'email': user0.email, 'username': user0.username, 'deleted': user0.deleted})
    hist_recs_count = user0.rec_history_count()
    logger.debug(f'user0 after deleted history count: {hist_recs_count}')
    for n in range(hist_recs_count):
        logger.debug(f'user0 after deleted history [{n}]: {user0.history.all()[0].changes_dict}')
    for rec in CustomUser.objects.all_with_deleted():
        logger.debug('After soft delete record 0: %(email)s: %(username)s, %(deleted)s', {'email': rec.email, 'username': rec.username, 'deleted': rec.deleted})
    assert user0.rec_history_count() == 2
    assert user0.rec_history_field_changed(0, 'deleted')  # record 0 is the latest
    assert user0.rec_history_field_was(0, 'deleted') == 'None'
    assert user0.rec_history_field_is_now(0, 'deleted') == user0.deleted.strftime("%Y-%m-%d %H:%M:%S.%f")

    # confirm we have one less
    assert CustomUser.objects.all_with_deleted().count() == 4
    assert CustomUser.objects.deleted_only().count() == 1

    # make sure the database does not allow duplicate emails for custom_users
    # tests the pre_save_call that copies the email into the username field
    # - this ensures that duplicate emails are not allowed at the database level
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            CustomUserFactory(
                email=test_users[0].email,
                username=test_users[0].username,
                first_name=test_users[0].first_name,
                last_name=test_users[0].last_name,
            )
    for rec in CustomUser.objects.all_with_deleted():
        logger.debug('After factory attempt to create duplicate of record 0: %(email)s: %(username)s, %(deleted)s', {'email': rec.email, 'username': rec.username, 'deleted': rec.deleted})
    assert CustomUser.objects.all_with_deleted().count() == 4
    assert CustomUser.objects.deleted_only().count() == 1
    test_users[0].undelete()
    assert CustomUser.objects.all_with_deleted().count() == 4
    assert CustomUser.objects.deleted_only().count() == 0
    logger.debug('Restored: %(email)s: %(username)s, %(deleted)s', {'email': test_users[0].email, 'username': test_users[0].username, 'deleted': test_users[0].deleted})

    ''' .. :Todo test to make sure that undeleted users can still log into the system and function properly'''
