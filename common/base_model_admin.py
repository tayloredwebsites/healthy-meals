from django.contrib import admin
from common.base_model import BaseModel
from common.base_model_base import BaseModelBaseAdmin


# class BaseModelAdmin(BaseModelBaseAdmin):
class BaseModelAdmin(admin.ModelAdmin):
    """ The BaseModelBase, BaseModel, BaseModelBaseAdmin, and BaseModelAdmin classes provide Soft Delete functionality, record versioning, and recording of who and when model records are added or changed.

    The BaseModelAdmin class is responsible for:
        - populating the created_at, created_by, updated_at, and updated_by fields
        - bringing in the BaseModelBaseAdmin to provide soft delete functionality administrative tools.

    Note::

        See the Note field in the BaseModelBase documentation for instruction to implement these base model classes.

        .. todo:: testing see: https://stackoverflow.com/questions/6498488/testing-admin-modeladmin-in-django#answer-54667823
    """

    def save_model(self, request, obj, form, change):
        """ update created_at, created_by, updated_at, and updated_by fields prior to save model save

        Notes:
            - pre and post code are in separate methods for DRY.  Used in model class, and model admin class

        created_by, and updated_by fields are set to the user making the request
        created_at, and updated_at fields are set to the exact same time.
        """
        BaseModel.pre_save(obj, change, request.user)

        super().save_model(request, obj, form, change)

        BaseModel.post_save(obj, change, request.user)
