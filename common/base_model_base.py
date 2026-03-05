"""Healthy Meals Web Site
Copyright (C) 2025 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/
https://github.com/tayloredwebsites/healthy-meals - healthy_meals/base_model_base.py


"""

import logging

from django.db import models
from django.utils import timezone
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE
from safedelete.admin import SafeDeleteAdmin # , highlight_deleted , SafeDeleteAdminFilter, highlight_deleted
from auditlog.models import AuditlogHistoryField

logger = logging.getLogger(__name__)

class BaseModelBaseAdmin(SafeDeleteAdmin):  # , admin.ModelAdmin
    """.. todo:: research to see if ModelAdmin is needed in BaseModelAdmin.  It is not needed for the CustomUserAdmin class."""


class BaseModelBase(SafeDeleteModel):
    """ The BaseModelBase, BaseModel, and BaseModelAdmin classes provide Soft Delete funcionality, record versioning, and recording of who and when model records are added or changed.

    BaseModelBase provides all of the following base model features, except for the created_by, and updated_by fields to avoid a circular reverence with the CustomUser model.
        - This prevents a circular reference because:
            - CustomUser would inherit from the base which would define the created_by, and updated_by fields.
            - The base model's created_by, and updated_by fields are foreign keys to CustomUser.
            - Thus a circular reference.
        - BaseModelBase is the base model for both BaseModel, and for CustomUser to provide DRY code to both models
        - Both BaseModel and CustomUser use this class (BaseModelBase) to inherit from.
        - Both the BaseModel and CustomUser classes independently define and manage the created_by, and the updated_by fields

    WHO AND WHEN, CREATED AND UPDATED RECORDS::

        - When changes are made are built into this BaseModelBase class.  It stores when a user has added or changed a record in the created_at, and the updated_at fields.
        - Who has changed a record is built into the BaseModel class, which inherits from this class.  The user who has created or changed a record is stored in the created_by, and updated_by fields.
        - Note: The actual update of these field values is done in the admin class "save_model" function. See the accounts/admin.py save_model function as an example of how to implement it in other apps.

    SOFT DELETE FUNCTIONALITY::

        - This abstract base class provide soft delete functionality included through django-safedelete (https://django-safedelete.readthedocs.io/en/latest/index.html)
        - In order for soft deletion each model manager class must inherit from SafeDeleteManager.  See the accounts/models.py CustomUserManager class as an example of how to implement it in other apps.
        - Available soft delete functions
            - all_with_deleted() # Show all model records including the soft deleted models.
            - deleted_only() # Only show the soft deleted model records.
            - all(**kwargs) -> django.db.models.query.QuerySet # Show deleted model records. (default: {None})
            - update_or_create(defaults=None, **kwargs) -> Tuple[django.db.models.base.Model, bool] # https://django-safedelete.readthedocs.io/en/latest/managers.html#safedelete.managers.SafeDeleteManager.update_or_create

    AUDITLOG VERSIONING HISTORY FUNCTIONALITY::

        - This abstract base class provides record history / versioning through django-auditlog (https://github.com/jazzband/django-auditlog)
        - this provides the ability to see the changes to fields (except fields excluded when registered in the model)
        - see: https://django-auditlog.readthedocs.io/en/latest/usage.html
        - In order for auditlog to properly function,it must be registered as the last line of the model.  See the statements at the end of the accounts/models.py file.

    Note::

        Implementation Notes:
        - In order for all models to consistently have Audit Log Versioning, Soft Deletes, and the recording of who and when records are created or updated and saved:
            - The model admin ("<AppClassName>Admin") class must inherit from the "BaseModelAdmin" class.
            - The model manager ("<AppClassName>Manager") class must inherit from the "SafeDeleteManager" class.
            - the model class must inherit from the "BaseModel" class.
                - Note: the accounts CustomUser class requires unique coding to avoid a circular reference.
            - The last line in the model class file ("<app>/models.py") needs to register the model with AuditLog as follows:

            .. code-block:: python

                # place as last line in model.py file to ensure it gets all changes into AuditLog
                auditlog.register(<ModelClassName>, exclude_fields=[
                    '<secret_field_name>', # protect this field for security reasons
                ]

    .. todo:: BaseModelBase considerations

        - review need for soft deletion, and see if is_active field (
        - consider moving record history methods from the model to a new base_model_history class.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
    )

    history = AuditlogHistoryField()  # history field to access audit log / record history

    _safedelete_policy = SOFT_DELETE_CASCADE  # soft deletes to not permanently delete them, and cascade soft deletes to child records.

    class Meta:
        abstract = True


    #########################################################################
    # Handy Methods for updating created_by, updated_by, created_at, and updated_at fields

    def get_user_from_request(self, request):
        """get the user from the request, or return None if there is no user in the request"""

        if self.objects.count() == 0:
            logger.debug('*** %(name)s::get_user_from_request - this is the first record, so setting user to None.', {'name': __name__})
            req_user = None
        else:
            req_user = request.user if request and request.user and request.user.id else None
            logger.debug('*** %(name)s::get_user_from_request called by %(user_id)s', {'name': __name__, 'user_id': req_user.id})
        return req_user

    def set_created_updated_by_at_fields(self, req_user):
        """ update created_by, updated_by, created_at, and updated_at fields prior to save model save

        created_by, and updated_by fields are set to the user making the request
        created_at, and updated_at fields are set to the exact same time.
        """
        time_now = timezone.now()
        if self.id is None:
            # this is a create, set the created fields
            self.created_by = req_user
            self.created_at = time_now
        # always set the updated fields
        self.updated_by = req_user
        self.updated_at = time_now
        return self


    #########################################################################
    # Handy methods for obtaining information from history (Auditlog)

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
            logger.debug('expected key error auditlog - no changes for field: %s', e)
            return ['None', 'None']
