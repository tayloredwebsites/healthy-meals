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

class BaseModel(SafeDeleteModel):
    """ BaseModel is abstract class to base all models in this project

    - has soft delete functionality included through django-safedelete
        - https://django-safedelete.readthedocs.io/en/latest/index.html
    - has record history / versioning through django-auditlog
        - https://github.com/jazzband/django-auditlog

    Note: The customized functions for soft deletion are only found in model manager classes
    Thus: to use the methods found in 'objects', their models must declare their custom manager based off of SafeDeleteManager
    See: accounts/models.py for an example

    - all_with_deleted() # Show all model records including the soft deleted models.
    - deleted_only() # Only show the soft deleted model records.
    - all(**kwargs) -> django.db.models.query.QuerySet # Show deleted model records. (default: {None})
    - update_or_create(defaults=None, **kwargs) -> Tuple[django.db.models.base.Model, bool] # https://django-safedelete.readthedocs.io/en/latest/managers.html#safedelete.managers.SafeDeleteManager.update_or_create
    """
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    history = AuditlogHistoryField() # audit log to maintain record history
    _safedelete_policy = SOFT_DELETE_CASCADE # cascade soft deletes of records as well as child records.

    class Meta:
        abstract = True


    def rec_history_count(self):
        '''Return the count of all of the history records for this user.'''
        return self.history.all().count()

    def rec_history_field_was(self, user_rec, field_name):
        '''Return a dictionary of the previous values for this field, for this record.'''
        rec = self.history.all()[user_rec]
        return self.__get_field_changes(rec,field_name)[0]

    def rec_history_field_is_now(self, user_rec, field_name):
        ''' What is the rec_history_field_is_now functionality?

        .. ToDo:: Research what the accounts.models.CustomUser.rec_history_field_is_now function was supposed to do.  Is this needed?

        '''
        rec = self.history.all()[user_rec]
        return self.__get_field_changes(rec,field_name)[1]

    def rec_history_field_changed(self, user_rec, field_name):
        '''Return the number of records that are maintained in CustomUser's history table.'''
        rec = self.history.all()[user_rec]
        changes = self.__get_field_changes(rec,field_name)
        # print(f'changes: {changes}')
        return changes[0] != changes[1]

    def __get_field_changes(self, hist_rec, field_name):
        '''Return a dictionary of the history for this record's field values.'''
        try:
            changes = hist_rec.changes_dict[field_name]
            # print(f'changes: {changes}')
            return changes
        except KeyError as e:
            # there was no change, audit log does not log values that do not change, so return array of None strings
            print(f'expected key error auditlog - no changes for field: {e}')
            return ['None', 'None']

