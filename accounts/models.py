"""
Healthy Meals Web Site
Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals

accounts/models.py - Accounts model (CustomUser records) for storing users customized to allow login by email, etc.

Mix in SafeDeleteManager into CustomUserManager for Soft Deletes using safedelete

- https://django-safedelete.readthedocs.io/en/latest/managers.html
- safe delete of custom users example found at;
- https://codeberg.org/mvlaev/Cars/src/branch/main/cars/users_app/models.py"
"""

import logging

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone

from allauth.account.models import EmailAddress
from safedelete.managers import SafeDeleteManager
from auditlog.registry import auditlog

from common.base_model_base import BaseModelBase
logger = logging.getLogger(__name__)

class CustomUserManager(SafeDeleteManager, UserManager):
    """Custom User model Manager class ('objects').

    Manager class for CustomUsers (Accounts).  Access to this class is through the 'objects' instance attribute of the CustomUser Class.

    Soft Delete of Users are implemented through SafeDelete.
    See: https://django-safedelete.readthedocs.io/en/latest/managers.html

    Args:
        param1 (class): SafeDeleteManager manager class
            - This is always needed when adding in the BaseModelBase class to the model class.
        param2 (class): UserManager  for CustomUser Abstract Class
    Args:
        param1 (class): BaseModelBase class
            - soft deletes using  django-safedelete
                - https://django-safedelete.readthedocs.io/en/latest/index.html
            - record history / versioning through django-auditlog
                - https://github.com/jazzband/django-auditlog
        param2 (class): AbstractUser from Allauth (from Lithium Starter)
            - see: https://docs.allauth.org/en/latest/
            - see: https://docs.allauth.org/en/latest/account/configuration.html


    Examples:
        $ cust_user = CustomUser()
            Returns: True
    """

    def create(self, *args, **kwargs):
        """Override the create method to ensure that the username is always set to the email address.

        This is required for this project because we are logging in by email address.
        """
        # logger.debug('*cu_m* %s::create - args: %s, kwargs: %s', __name__, args, kwargs)
        return super(CustomUserManager, self).create(*args, **kwargs)


#########################################################################
# Model class for CustomUser
# @admin.register(CustomUser)
class CustomUser(BaseModelBase, AbstractUser):  # pylint: disable=R0902
    """CustomUser model - Abstract User customized to allow login by email

    Add in abstract BaseModelBase to provide:

    Args:
        param1 (class): BaseModelBase class
            - soft deletes using  django-safedelete
                - https://django-safedelete.readthedocs.io/en/latest/index.html
            - record history / versioning through django-auditlog
                - https://github.com/jazzband/django-auditlog
        param2 (class): AbstractUser from Allauth (from Lithium Starter)
            - see: https://docs.allauth.org/en/latest/
            - see: https://docs.allauth.org/en/latest/account/configuration.html
    """

    #########################################################################
    # Field Definitions (done here because we are not inheriting from BaseModel)

    created_by = models.ForeignKey(
        'self',
        related_name='self_created_by',
        editable=False,
        on_delete=models.PROTECT,
        null=True,  # temporarily allow null to be sure required user exists already (issue on first user created)
    )  # same as what common.BaseModel does

    updated_by = models.ForeignKey(
        'self',
        related_name='self_updated_by',
        editable=False,
        on_delete=models.PROTECT,
        null=True,  # temporarily allow null to be sure required user exists already (issue on first user created)
    )  # same as what common.BaseModel does

    objects = CustomUserManager()

    def __str__(self):
        """What to print when printing a user's record."""
        # fields = [field.name for field in self._meta.fields if field.name != 'password']
        # return ', '.join(f"{field}: {getattr(self, field)}" for field in fields)
        return f'CustomUser: {self.id} - {self.email}: {self.last_name}, {self.first_name}, deleted: {self.deleted}'  # pylint: disable=E1101

    def __format__(self, print_format):
        """selectively choose print format.  e.g. print(f"{user0:detail}") """
        if print_format == "detail":
            fields = [field.name for field in self._meta.fields if field.name != 'password' or field.name.startswith('_')]
            ret_str = '\naccounts CustomUser record:'
            # loop through the fields (except password)
            for field in fields:
                val = getattr(self, field)
                if val is None:
                    ret_str += f'\n  {field}: None'
                else:
                    ret_str += f'\n  {field}: {getattr(self, field)}'
            return ret_str  # default to __str__ style print
        return str(self)

    #########################################################################
    # Save method override needed for the fields added
    def clean(self, *args, **kwargs):
        """See if we can get an error do display in Admin console"""
        # logger.debug(f"""*cu* {__name__}::clean -
        #     CustomUser before:
        #     self:detail
        # """)
        # force email to match username before validation.
        # This is required for this project.
        if self.email == '' and self.username != '':
            # allow entering email under the username field in the admin interface
            self.email = self.username
        else:
            # forcing the username to be the email address always - required in this project
            self.username = self.email

        # do validations
        super().clean()
        # logger.debug(f"""*cu* {__name__}::clean -
        #     CustomUser before:
        #     self:detail
        # """)
        # if CustomUser.objects.filter(email=self.email).exists():
        #     raise ValidationError("This email is already in use.")

    #########################################################################
    # Save method override needed for the fields added
    def save(self, *args, **kwargs):
        """Force the username field to be the same as the email field

        Prevent duplication of email addresses in the CustomUser model at the database level.

        - We do not want duplicate emails in the database, because we are logging in by email address
        - To prevent this, we are ensuring that all users username are (a copy of) their email address
        - Thus the good mechanism for preventing duplicate usernames will be used by copying email addresses to the username field
        - ``Warning``: do not use this CustomUser model if you wish to have usernames that are other than the user's email address

        .. todo:: test to ensure that user is always set to the request user, not the prior one.
        """

        # get the current user from the form or request being used
        # if self.request and self.request.user.is_authenticated:
        # https://www.vindevs.com/blog/how-to-get-the-current-user-in-a-django-model-p64/
        print(f"*cu_s* {__name__}::save - args: {args}, kwargs: {kwargs}")

        # Fill in the created_by and updated_by fields if not set, by using the _req_user temporary field.
        logger.debug(f"*cu_s* %s::save - self - %s", __name__, format(self, 'detail'))
        auth_user = None

        # Code to set auth_user to the request user if available, otherwise use the updated_by user if available
        # - Best Practice: set updated-by to None if updating user is unknown, so that it will be set by the request user.
        auth_user = self.get_user_from_request(self, self.request) if hasattr(self, 'request') else self.updated_by  # use the updated_by user if no request user is available
        logger.debug('*** %(name)s::save - auth_user: %(auth_user)s', {'name': __name__, 'auth_user': auth_user})
        self = self.set_created_updated_by_at_fields(auth_user)

        # logger.debug('*cu_s* created_by: %s, updated_by: %s', self.created_by, self.updated_by)
        logger.debug('*cu_s* save CustomUser - self: %s', f'{self:detail}')

        # perform all pre-save field changes (DRY)
        # CustomUser.pre_save_call(self, auth_user)
        # logger.debug(f'*cu_s* {__name__}::save - after pre-save CustomUser: {self:detail}')

        # ensure staff status is set when superuser is set, and vice versa
        if self.is_superuser and not self.is_staff:
            self.is_staff = True
        elif self.is_staff and not self.is_superuser:
            self.is_superuser = True

        logger.debug('*cu_s* CustomUser before save - _req_user: %s, auth_user: %s, updated_by: %s', getattr(self, '_req_user', '-'), auth_user, self.updated_by)
        super().save(*args, **kwargs)
        logger.debug('*cu_s* CustomUser after save - _req_user: %s, auth_user: %s, updated_by: %s', getattr(self, '_req_user', '-'), auth_user, self.updated_by)


    #########################################################################
    # Handy methods for obtaining information from history (Auditlog)

    def name_or_email(self):
        """Return the user's full name, otherwise return their email."""
        if self.first_name != '' and self.last_name != '':
            return f"{self.first_name} {self.last_name}"
        logger.debug('missing full name, using user email: %s', self.email)
        return self.email

    #########################################################################
    # monkey patches

    def patched_email_address_format(self, print_format):
        """selectively choose print format.  e.g. print(f"{user_email_rec:detail}")

        .. todo:: test normal and detailed printouts printouts
        """

        if print_format == "detail":
            fields = [field.name for field in self._meta.fields]  # if field.name != 'password']
            ret_str = '\naccounts CustomUser Email record:'
            # loop through the fields (except password)
            for field in fields:
                val = getattr(self, field)
                if val is None:
                    ret_str += f'\n  {field}: None'  # pragma: no cover
                else:
                    ret_str += f'\n  {field}: {val}'
            return ret_str + '\n'
        return str(self)  # default to __str__ style print

    EmailAddress.__format__ = patched_email_address_format


#########################################################################
# Place as last line in file to ensure it gets all changes into AuditLog.
# - This statement is needed when adding the BaseModelBase or BaseModel abstract class.
# - This statement must be customized to choose which sensitive fields must be protected.
auditlog.register(CustomUser, exclude_fields=[
    'password',  # protect this field for security reasons
    'last_login',  # do not update audit log for each login
])
