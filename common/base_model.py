"""
Healthy Meals Web Site
Copyright (C) 2025 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals - healthy_meals/base_model.py


This base model will be the base for all models exceipt for the CustomUser model.
The CustomUser model will inherit from BaseModelBase to avoid a circular reference with the created_by, and updated_by fields.

"""
# import logging

# from django.db import models
# from django.utils import timezone

# from common.base_model_base import BaseModelBase, BaseModelBaseAdmin
# from accounts.models import CustomUser

# logger = logging.getLogger(__name__)

# # class BaseModelAdmin(admin.ModelAdmin):
# class BaseModelAdmin(BaseModelBaseAdmin):
#     """ The BaseModelBase, BaseModel, BaseModelBaseAdmin, and BaseModelAdmin classes provide Soft Delete functionality, record versioning, and recording of who and when model records are added or changed.

#     The BaseModelAdmin class is responsible for:
#         - populating the created_at, created_by, updated_at, and updated_by fields
#         - bringing in the BaseModelBaseAdmin to provide soft delete functionality administrative tools.

#     Note::

#         See the Note field in the BaseModelBase documentation for instruction to implement these base model classes.

#         .. todo:: testing see: https://stackoverflow.com/questions/6498488/testing-admin-modeladmin-in-django#answer-54667823
#     """

#     def save_model(self, request, obj, form, change):
#         """ update created_at, created_by, updated_at, and updated_by fields prior to save model save

#         Notes:
#             - pre and post code are in separate methods for DRY.  Used in model class, and model admin class
#         """
#         logger.debug('*** %(name)s::save - %(user_id)s is calling save_model: %(obj)s', {'name': __name__, 'user_id': request.user.id, 'obj': self})
#         #
#         # BaseModel.pre_save_call(obj, request.user)

#         super().save_model(request, obj, form, change)

#         # BaseModel.post_save(obj, request.user)


# class BaseModel(BaseModelBase):
#     """ The BaseModel and BaseModelBase abstract classes provide Soft Delete funcionality, record versioning, and recording of who and when model records are added or changed.

#     Note:: This is commented out until another model besides accounts.CustomUser is created to inherit from this base model.

#     The BaseModel is the base model for all model classes to inherit from (except for CustomUser - see below.)

#     WHO AND WHEN OF RECORD CREATES AND UPDATES::

#         - When changes are made are built into this BaseModelBase class.  It stores when a user has added or changed a record in the created_at, and the updated_at fields.

#     SOFT DELETE FUNCTIONALITY

#         - See the BaseModelBase class which this class inherits from, which provides soft delete functionality included through django-safedelete (https://django-safedelete.readthedocs.io/en/latest/index.html)

#     AUDITLOG VERSIONING HISTORY FUNCTIONALITY

#         - See the BaseModelBase class which this class inherits from, which provides record history / versioning through django-auditlog (https://github.com/jazzband/django-auditlog)

#     Note::

#         See the Note field in the BaseModelBase documentation for instruction to implement these base model classes.
#     """

    # class Meta:
    #     abstract = True

    # # Fields added in this abstract model
    # created_by = models.ForeignKey(
    #     CustomUser,
    #     related_name='base_created_by',
    #     editable=False,
    #     on_delete=models.PROTECT,
    #     null=True,  # temporarily allow null to be sure required user exists already (issue on first user created)
    # )
    # updated_by = models.ForeignKey(
    #     CustomUser,
    #     related_name='base_updated_by',
    #     editable=False,
    #     on_delete=models.PROTECT,
    #     null=True,  # temporarily allow null to be sure required user exists already (issue on first user created)
    # )

    # # Save method override needed for the fields added
    # def save(self, *args, **kwargs):
    #     """ update created_at, created_by, updated_at, and updated_by fields prior to save model save

    #     Notes:
    #         - BaseModelBase does not have a save method override in it.
    #         - pre and post code are in separate methods for DRY.  Used in model class, and model admin class

    #     References:
    #         - https://www.w3tutorials.net/blog/django-how-to-get-current-user-in-admin-forms/#method-3-override-save_model-for-post-save-actions

    #     created_by, and updated_by fields are set to the user making the request
    #     created_at, and updated_at fields are set to the exact same time.
    #     """
    #     logger.debug('*** %(name)s::save: %(self)s', {'name': __name__, 'self': self})

    #     auth_user = get_user_from_request(self, self.request)
    #     logger.debug('*** %(name)s::save - auth_user: %(auth_user)s', {'name': __name__, 'auth_user': auth_user})
    #     BaseModel.set_created_updated_by_at_fields(auth_user)

    #     super().save(*args, **kwargs)
