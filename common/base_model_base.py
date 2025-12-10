# Healthy Meals Web Site
# Copyright (C) 2025 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
# Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/
# https://github.com/tayloredwebsites/healthy-meals - healthy_meals/base_model_base.py

from django.db import models
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE
from auditlog.models import AuditlogHistoryField
from safedelete.admin import SafeDeleteAdmin, highlight_deleted  # , SafeDeleteAdminFilter, highlight_deleted


class BaseModelBaseAdmin(SafeDeleteAdmin):
    pass


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
        - In order for soft deletion each model manager classe must inherit from SafeDeleteManager.  See the accounts/models.py CustomUserManager class as an example of how to implement it in other apps.
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

    history = AuditlogHistoryField()  # audit log to maintain record history

    _safedelete_policy = SOFT_DELETE_CASCADE  # soft deletes to not permanently delete them, and cascade soft deletes to child records.

    class Meta:
        abstract = True

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
            print(f'expected key error auditlog - no changes for field: {e}')
            return ['None', 'None']
