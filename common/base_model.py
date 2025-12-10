'''
Healthy Meals Web Site
Copyright (C) 2025 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals - healthy_meals/base_model.py
'''

from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE
from safedelete.managers import SafeDeleteManager
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
from django.utils import timezone

from common.base_model_base import BaseModelBase
from accounts.models import CustomUser


class BaseModel(BaseModelBase):
    """ The BaseModel and BaseModelBase abstract classes provide Soft Delete funcionality, record versioning, and recording of who and when model records are added or changed.

    The BaseModel class provides the created_by, and updated_by fields that could not be implemented in BaseModelBase because of a circular reference.

    WHO AND WHEN OF RECORD CREATES AND UPDATES::

        - When changes are made are built into this BaseModelBase class.  It stores when a user has added or changed a record in the created_at, and the updated_at fields.

    SOFT DELETE FUNCTIONALITY

        - See the BaseModelBase class which this class inherits from, which provides soft delete functionality included through django-safedelete (https://django-safedelete.readthedocs.io/en/latest/index.html)

    AUDITLOG VERSIONING HISTORY FUNCTIONALITY

        - See the BaseModelBase class which this class inherits from, which provides record history / versioning through django-auditlog (https://github.com/jazzband/django-auditlog)

    Note::

        See the Note field in the BaseModelBase documentation for instruction to implement these base model classes.
    """

    class Meta:
        abstract = True

    # Fields added in this abstract model
    created_by = models.ForeignKey(
        CustomUser,
        related_name='base_created_by',
        editable=False,
        on_delete=models.PROTECT,
        null=True,  # temporarily allow null to be sure required user exists already (issue on first user created)
    )
    updated_by = models.ForeignKey(
        CustomUser,
        related_name='base_updated_by',
        editable=False,
        on_delete=models.PROTECT,
        null=True,  # temporarily allow null to be sure required user exists already (issue on first user created)
    )

    # Save method override needed for the fields added
    def save(self, *args, **kwargs):
        """ update created_at, created_by, updated_at, and updated_by fields prior to save model save

        Notes:
            - BaseModelBase does not have a save method override in it.
            - pre and post code are in separate methods for DRY.  Used in model class, and model admin class

        References:
            - https://www.w3tutorials.net/blog/django-how-to-get-current-user-in-admin-forms/#method-3-override-save_model-for-post-save-actions

        created_by, and updated_by fields are set to the user making the request
        created_at, and updated_at fields are set to the exact same time.
        """

        is_changed = self.id is not None

        auth_user = None
        if self.request and self.request.user.is_authenticated:
            auth_user = self.request.user

        # perform all pre-save field changes (DRY)
        BaseModel.pre_save(self, is_changed, auth_user)

        super().save(*args, **kwargs)

        print(f'*** common/base_model_admin.save_model post-save')
        BaseModel.post_save(new_self, is_changed, auth_user)

    # pre-save code used by save method for DRY (used by BaseModel, and by BaseModelAdmin)
    def pre_save(self, is_changed, user=None):
        """ all presave update code needed for all models inheriting from BaseModel

        created_by, and updated_by fields are set to the user making the request
        created_at, and updated_at fields are set to the exact same time.
        """
        print(f'*** common/base_model.save pre-save')
        if CustomUser.count() == 0:
            # no users yes, can't save user yet
            user = None
        time_now = timezone.now()
        if self.id == None:
            # this is a create, set the created fields
            self.created_by = user
            self.created_at = time_now
        # always set the updated fields
        self.updated_by = user
        self.updated_at = time_now
        return self

    # post-save code used by save method for DRY (used by BaseModel, and by BaseModelAdmin)
    def post_save(self, is_changed, user=None):
        """ all postsave update code needed for all models inheriting from BaseModel """
        # print(f'*** common/base_model_admin.save_model post-save')

    def rec_history_count(self):
        """Return the count of all of the history records for this user."""
        return self.history.all().count()

    def rec_history_field_was(self, user_rec, field_name):
        """Return a dictionary of the previous values for this field, for this record."""
        rec = self.history.all()[user_rec]
        return self.__get_field_changes(rec, field_name)[0]

    def rec_history_field_is_now(self, user_rec, field_name):
        """Return the latest history record value for this field (should be identical to current field value)"""
        rec = self.history.all()[user_rec]
        return self.__get_field_changes(rec, field_name)[1]

    def rec_history_field_changed(self, user_rec, field_name):
        """Return the number of records that are maintained in CustomUser's history table."""
        rec = self.history.all()[user_rec]
        changes = self.__get_field_changes(rec, field_name)
        # print(f'changes: {changes}')
        return changes[0] != changes[1]

    def __get_field_changes(self, hist_rec, field_name):
        """Return a dictionary of the history for this record's field values."""
        try:
            changes = hist_rec.changes_dict[field_name]
            # print(f'changes: {changes}')
            return changes
        except KeyError as e:
            # there was no change, audit log does not log values that do not change, so return array of None strings
            print(f'expected key error auditlog - no changes for field: {e}')
            return ['None', 'None']
