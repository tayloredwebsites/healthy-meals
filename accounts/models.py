""" Accounts model (CustomUser records) for storing users customized to allow login by email, etc.

Mix in SafeDeleteManager into CustomUserManager for Soft Deletes using safedelete

- https://django-safedelete.readthedocs.io/en/latest/managers.html
- safe delete of custom users example found at;
- https://codeberg.org/mvlaev/Cars/src/branch/main/cars/users_app/models.py"

"""
from django.contrib.auth.models import AbstractUser, UserManager
from common.base_model import BaseModel
# from safedelete.models import SafeDeleteModel
# from safedelete.models import SOFT_DELETE_CASCADE
from safedelete.managers import SafeDeleteManager
from auditlog.registry import auditlog
# from auditlog.models import AuditlogHistoryField


class CustomUserManager(SafeDeleteManager, UserManager):
    """Custom User model Manager class ('objects').

    Manager class for CustomUsers (Accounts).  Access to this class is through the 'objects'
    instance attribute of the CustomUser Class.

    Soft Delete of Users are implemented through SafeDelete.
    See: https://django-safedelete.readthedocs.io/en/latest/managers.html

    Args:
        param1 (class): SafeDelete manager class mixin
        param2 (class): UserManager  for CustomUser Abstract Class

    """
    def all_deleted(self):
        """Returns all soft deleted customuser records.

        .. ToDo:: replace accounts.models.CustomUserManager.all_deleted with SafeDeleteManager.deleted_only()

            - see: https://django-safedelete.readthedocs.io/en/latest/managers.html
            - note: these functions are only found in model manager classes
            -  thus: all models must declare their custom manager based off of SafeDeleteManager

        No arguments are passed to this function when calling it

        Returns:
            recordset: The soft deleted custom user records.

        Example:

            .. code-block:: python

                # Print out all deleted records
                for rec in Account.all_deleted():
                    print(rec)

        """
        return self.all_with_deleted().filter(deleted__isnull=False)


class CustomUser(BaseModel, AbstractUser):
    '''CustomUser model - Abstract User customized to allow login by email

    Mix in BaseModel to provide:
    - soft deletes using  django-safedelete
        - https://django-safedelete.readthedocs.io/en/latest/index.html
    - record history / versioning through django-auditlog
        - https://github.com/jazzband/django-auditlog
    '''
    objects = CustomUserManager()

    def name_or_email(self):
        '''Return the user's full name, otherwise return their email.'''
        if self.first_name != '' and self.last_name != '':
            return "{fname} {lname}".format(fname=self.first_name, lname=self.last_name)
        else:
            print(f'missing full name, using user email: {self.email}')
            return self.email
    pass

    def __str__(self):
        '''What to print when printing a user's record.'''
        # fields = [field.name for field in self._meta.fields if field.name != 'password']
        # return ', '.join(f"{field}: {getattr(self, field)}" for field in fields)
        return f'{self.email} - {self.last_name}, {self.first_name}'

# place as last line in file to ensure it gets all changes into AuditLog
auditlog.register(CustomUser, exclude_fields=[
    'password', # protect this field for security reasons
    'last_login', # do not update audit log for each login
    ]
)
