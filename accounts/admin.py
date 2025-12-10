from django.contrib import admin
from common.base_model_base import BaseModelBaseAdmin
from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter, highlight_deleted

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseModelBaseAdmin):
    """ Accounts (CustomUser) Administration customization

    Notes::

        - for allauth documentation (which this app uses:
            - see: https://docs.allauth.org/en/latest/
            - see: https://docs.allauth.org/en/latest/account/configuration.html
        - for admin list page customization:
            - https://django.wiki/snippets/admin/admin-list-display/
            - https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display

    .. todo::
        - review add_form, form, and model variables in CustomUserAdmin class.  What are these?  Should something else be used, or should they be removed?
        - Testing, see: https://stackoverflow.com/questions/6498488/testing-admin-modeladmin-in-django#answer-54667823
        - consider using date_hierarchy for the change listing page: docs.djangoproject.com/en/6.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy
    """
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = CustomUser

    # specify the fields in the Admin List custom users
    list_display = (
        "email",
        "first_name",
        "last_name",
        "f_superuser",
        # "f_staff",
        "f_deleted",
        # "is_active",
        "f_updated_at",
        "updated_by",
    )

    def f_superuser(self, obj):
        """customize the is_superuser column field display

        Note: set f_superuser.short_description for the column title
        """
        return obj.is_superuser

    # customize the is_superuser column header
    f_superuser.short_description = "Superuser"  # shorter column title

    def f_staff(self, obj):
        """customize the is_staff column field display

        Note: set f_staff.short_description for the column title
        """
        return obj.is_staff

    # customize the is_staff column header
    f_staff.short_description = "Staff"  # shorter column title

    def f_deleted(self, obj):
        """customize the deleted column field display

        Note: set f_deleted.short_description for the column title
        """
        if obj.deleted == None:
            return ''
        else:
            return f'{obj.deleted.strftime("%Y-%m-%d")}'

    # customize the deleted column header
    f_deleted.short_description = "Deleted"

    def f_updated_at(self, obj):
        """customize the updated_at column field display

        Note: set f_updated_at.short_description for the column title
        """
        if obj.updated_at == None:
            return ''
        else:
            return f'{obj.updated_at.strftime("%Y-%m-%d")}'

    # customize the updated_at column field display and column header
    f_updated_at.short_description = "Updated at"

    def save_model(self, request, obj, form, change):
        """Force the username field to be the same as the email field in the database

        Prevent duplication of email addresses in the CustomUser model at the database level.

            - it was possible to have duplicate emails in the database, thus leaving a potential issue with duplicate emails in the database
            - We want to prevent duplicate emails in the database, because we are logging in by email address
            - ``Warning``: do not use this CustomUser model if you wish to have usernames that are other than the user's email address
            - see: https://docs.allauth.org/en/latest/
            - see: https://docs.allauth.org/en/latest/account/configuration.html

        We are using the CustomUser pre_save signal to force username field to be set to the records email field value for all CustomUser records
        """
        CustomUser.pre_save(obj, change, request.user)

        super().save_model(request, obj, form, change)

        CustomUser.post_save(obj, change, request.user)
