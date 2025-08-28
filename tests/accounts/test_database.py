
import pytest

from .factories import CustomUserFactory

from accounts.models import CustomUser

from django.db import IntegrityError, transaction

@pytest.mark.django_db
def test_user_soft_delete():
    '''Ensure soft deletes and undeletes update the database properly

        - emails are ensured to be unique,
        - CustomUser prints out as expected,
        - all_deleted (custom function) return the deleted custom users
        - run as large test to minimize database setup and teardown

    '''
    # get starting user record count
    print('Starting TestUserModel::test_user_soft_delete')
    count = CustomUser.objects.count()
    # confirm no users
    assert count == 0
    # create 4 test users
    test_users = CustomUserFactory.create_batch(4)
    # confirm we now have 4 more
    assert count + 4 == CustomUser.objects.count()
    user0 = test_users[0]
    print(f'user0 history count: {user0.rec_history_count()}')
    assert user0.rec_history_count() == 1
    assert not user0.rec_history_field_changed(0, 'deleted')
    # ensure print output of CustomUser is correct
    assert user0.__str__() == f'{user0.email} - {user0.last_name}, {user0.first_name}'
    print(f'As Created: {user0.email}: {user0.username}, {user0.deleted}')
    # soft delete the first user
    user0.delete()
    print(f'Soft Deleted: {user0.email}: {user0.username}, {user0.deleted}')
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

    # confirm we have one less
    assert CustomUser.objects.all_with_deleted().count() == 4
    assert CustomUser.objects.all_deleted().count() == 1

    # make sure the database does not allow duplicate emails for custom_users
    # tests the pre_save signal that copies the email into the username field
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
        print(f'After factory attempt to create duplicate of record 0: {rec.email}: {rec.username}, {rec.deleted}')
    assert CustomUser.objects.all_with_deleted().count() == 4
    assert CustomUser.objects.all_deleted().count() == 1
    test_users[0].undelete()
    assert CustomUser.objects.all_with_deleted().count() == 4
    assert CustomUser.objects.all_deleted().count() == 0
    print(f'Restored: {test_users[0].email}: {test_users[0].username}, {test_users[0].deleted}')

    ''' .. :Todo test to make sure that undeleted users can still log into the system and function properly'''