""" Accounts model (CustomUser records) for storing users customized to allow login by email, etc.

Mix in SafeDeleteManager into CustomUserManager for Soft Deletes using safedelete

- https://django-safedelete.readthedocs.io/en/latest/managers.html
- safe delete of custom users example found at;
- https://codeberg.org/mvlaev/Cars/src/branch/main/cars/users_app/models.py"
"""
import logging

from allauth.account.models import EmailAddress
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
# from common.base_model import BaseModel
# from safedelete.models import SafeDeleteModel
# from safedelete.models import SOFT_DELETE_CASCADE
from safedelete.managers import SafeDeleteManager
from auditlog.registry import auditlog

from common.base_model_base import BaseModelBase


# from auditlog.models import AuditlogHistoryField


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


#########################################################################
# Model class for CustomUser
class CustomUser(BaseModelBase, AbstractUser):
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
        return f'CustomUser: {self.id} - {self.email}: {self.last_name}, {self.first_name}, deleted: {self.deleted}'

    def __format__(self, print_format):
        """selectively choose print format.  e.g. print(f"{user0:detail}") """
        if print_format == "detail":
            fields = [field.name for field in self._meta.fields if field.name != 'password']
            ret_str = '\naccounts CustomUser record:'
            # loop through the fields (except password)
            for field in fields:
                val = getattr(self, field)
                if val is None:
                    ret_str += f'\n  {field}: None'
                else:
                    ret_str += f'\n  {field}: {getattr(self, field)}'
            return ret_str  # default to __str__ style print
        else:
            return str(self)

    #########################################################################
    # Save method override needed for the fields added
    def save(self, *args, **kwargs):
        """Force the username field to be the same as the email field

        Prevent duplication of email addresses in the CustomUser model at the database level.

        - We do not want duplicate emails in the database, because we are logging in by email address
        - To prevent this, we are ensuring that all users username are (a copy of) their email address
        - Thus the good mechanism for preventing duplicate usernames will be used by copying email addresses to the username field
        - ``Warning``: do not use this CustomUser model if you wish to have usernames that are other than the user's email address
        """

        # get the current user from the form being used
        # if self.request and self.request.user.is_authenticated:
        # https://www.vindevs.com/blog/how-to-get-the-current-user-in-a-django-model-p64/

        auth_user = kwargs.pop('user', None)
        # print(f'*** auth_user: {auth_user}')
        # print(f'*** CustomUser.self: {self:detail}')

        is_changed = self.id != None

        # perform all pre-save field changes (DRY)
        CustomUser.pre_save(self, is_changed, auth_user)

        super().save(*args, **kwargs)

        print(f'*** common/base_model_admin.save_model post-save')
        CustomUser.post_save(self, is_changed, auth_user)

    # -------------------------------------------------------------------------------------------------------------------
    # pre-save code used by save method for DRY (used by CustomUser, and by CustomUserAdmin)
    def pre_save(self, is_changed, user=None):
        """All presave update code needed for CustomUser model are here (DRY).

        Ensure that username is a copy of the email field, for logging in by unique email
        """
        logger = logging.getLogger(__name__)
        logger.debug('accounts/models.CustomUser.custom_user_pre_save')
        logger.debug(f'''custom user:
            {self:detail}''')
        if self.username != self.email:
            logger.debug(f"{self.__class__.__name__}::pre_save changed username from {self.username} to {self.email}")
            self.username = self.email
        return self

    # -------------------------------------------------------------------------------------------------------------------
    # post-save code used by save method for DRY (used by CustomUser, and by CustomUserAdmin)
    def post_save(self, is_changed, user=None):
        """All postsave update code needed for CustomUser model to go here (DRY)."""
        pass

    #########################################################################
    # Handy methods for obtaining information from history (Auditlog)

    def name_or_email(self):
        """Return the user's full name, otherwise return their email."""
        if self.first_name != '' and self.last_name != '':
            return "{fname} {lname}".format(fname=self.first_name, lname=self.last_name)
        else:
            print(f'missing full name, using user email: {self.email}')
            return self.email

    #########################################################################
    # monkey patches

    def patched_email_address_format(self, print_format):
        """selectively choose print format.  e.g. print(f"{user_email_rec:detail}") """
        if print_format == "detail":
            fields = [field.name for field in self._meta.fields if field.name != 'password']
            ret_str = '\naccounts CustomUser record:'
            # loop through the fields (except password)
            for field in fields:
                val = getattr(self, field)
                if val is None:
                    ret_str += f'\n  {field}: None'  # pragma: no cover
                else:
                    # This is just in case
                    ret_str += f'\n  {field}: {getattr(self, field)}'
            return ret_str  # default to __str__ style print
        else:  # pragma: no cover
            return str(self)

    EmailAddress.__format__ = patched_email_address_format


#########################################################################
# Place as last line in file to ensure it gets all changes into AuditLog.
# - This statement is needed when adding the BaseModelBase or BaseModel abstract class.
# - This statement must be customized to choose which sensitive fields must be protected.
auditlog.register(CustomUser, exclude_fields=[
    'password',  # protect this field for security reasons
    'last_login',  # do not update audit log for each login
])
