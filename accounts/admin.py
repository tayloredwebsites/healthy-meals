"""
Healthy Meals Web Site
Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals

accounts/admin.py - Accounts admin interface customization for CustomUser records
"""

import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from common.base_model_base import BaseModelBaseAdmin
# from safedelete.admin import SafeDeleteAdmin, SafeDeleteAdminFilter, highlight_deleted

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

logger = logging.getLogger(__name__)

class CustomUserAdmin(UserAdmin):  # BaseModelBaseAdmin):
    """ Accounts (CustomUser) Administration customization

    Args::

        param1 (class): UserAdmin from Django for handling the extra add user functionality
            - see: https://stackoverflow.com/questions/15012235/using-django-auth-useradmin-for-a-custom-user-model
        param2 (class): BaseModelBaseAdmin class
            - provides soft deletes from django-safedelete (used in all models)
            - see: django-safedelete.readthedocs.io/en/latest/index.html

    Notes::

        - note no need for record history / versioning in admin
                - https://github.com/jazzband/django-auditlog
        - for allauth documentation (which this app uses:
            - see: https://docs.allauth.org/en/latest/
            - see: https://docs.allauth.org/en/latest/account/configuration.html

    .. todo:: CustomUserAdmin items to do:
        - add session timeout, defaulting to 30 minutes.
        - evaluate need to provide SafeDeleteAdmin functionality (through BaseModelBaseAdmin?)
    """

    model = CustomUser
    date_hierarchy = "updated_at"

    """customize the built in admin user add and change forms
    - shows the message near the top of the Add Custom User page: NOTE: 'username' is automatically set to 'email'
    - see: https://docs.djangoproject.com/en/6.0/ref/contrib/admin/#set-up-your-projects-admin-template-directories
    - https://docs.djangoproject.com/en/6.0/ref/contrib/admin/#overriding-vs-replacing-an-admin-template
    """
    # change_form_template = 'admin/accounts/custom_user/change_form_pwd_reset.html'
    # add_form_template = 'admin/accounts/custom_user/add_form_errors.html'

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm  # Not creating own custom forms, but  using exising admin form tooling

    readonly_fields = (
        'id',
        # 'username',  # this prevents adding users, because add user form does not include email
        'is_active',
        'is_staff',
    )

    ####################################################################################################################
    # grouping of fields to display in add and modify form

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.

    # readonly_fields = ('id', 'username', 'is_staff', 'created_at', 'created_by', 'updated_at', 'updated_by')
    # fieldsets = [
    #     ('Account info', {'fields': ['id', 'email', 'username', 'password']}),
    #     ('Personal info', {'fields': ['first_name', 'last_name']}),
    #     ('Permissions', {'fields': ['is_superuser', 'is_staff']}),
    #     ('Metadata', {'fields': ['created_at', 'created_by', 'updated_at', 'updated_by']}),
    # ]

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.

    # add_fieldsets = [
    #     ('Account info', {'fields': ['email', 'username', 'password1', 'password2']}),
    #     ('Personal info', {'fields': ['first_name', 'last_name']}),
    #     ('Permissions', {'fields': ['is_superuser', 'is_staff']}),
    # ]

    ####################################################################################################################
    # customizations of the list display

    """Specify the fields in the Custom Users Admin List custom users for admin list page customization:
        - https: // django.wiki / snippets / admin / admin - list - display /
        - https: // docs.djangoproject.com / en / dev / ref / contrib / admin /  # django.contrib.admin.ModelAdmin.list_display
    """
    list_display = (
        "email",
        # "username",
        "first_name",
        "last_name",
        "f_superuser",
        "f_staff",
        # "is_staff",
        "f_deleted",
        # "is_active",
        "f_updated_at",
        "f_updated_by",
    )

    def f_superuser(self, obj):
        """customize the listing page is_superuser column header and fieldy"""
        return obj.is_superuser

    f_superuser.short_description = "Superuser"  # shorter column title

    def f_staff(self, obj):  # pragma: no cover
        """customize the listing page is_staff column header and field
        - this is not currently used
        - when using this, also set f_staff.short_description for the column title
        """
        return obj.is_staff

    f_staff.short_description = "Staff"  # shorter column title

    def f_deleted(self, obj):
        """customize the listing page deleted column header and field"""
        # print(f'*cua* admin.py CustomUser id: {obj.id}, f_deleted: {obj.deleted}, f_deleted is None: {obj.deleted is None}')
        if obj.deleted is None:
            return ''
        return f'{obj.deleted.strftime("%Y-%m-%d")}'

    f_deleted.short_description = "Deleted"

    def f_updated_at(self, obj):
        """customize the listing page updated_at column header and field"""
        if obj.updated_at is None:
            return ''  # pragma: no cover  # this should never happen, but just in case
        return f'{obj.updated_at.strftime("%Y-%m-%d")}'

    f_updated_at.short_description = "Updated at"

    def f_updated_by(self, obj):
        """customize the listing page updated_by column header and field"""
        if obj.updated_by is None:
            return ''  # pragma: no cover  # this should never happen, but just in case
        return f'{obj.updated_by.id}'

    f_updated_by.short_description = "Updated by"

    ####################################################################################################################
    # save_model enhancement

    def save_model(self, request, obj, form, change):
        """Enhance Admin CustomUser save_model method to pass in the request user as a temporary field in the model record.
        - passing in _req_user to the model record so updated_by and created_by can be set to the user making the request
        - otherwise, it gets lost between the admin save_model call with the request passed, and the save, which doesn't
        """
        logger.debug('*cua* %s - save_model: self: %s', __name__, self)
        logger.debug('*cua* %s - save_model: obj: %s', __name__, f'{obj:detail}')

        obj.updated_by = request.user  # this is to pass the request user to the model record save function, to set created_by and updated_by
        logger.debug("*cua* %s - before super().save_model: obj': %s", __name__, format(obj, 'detail'))
        super().save_model(request, obj, form, change)
        logger.debug("*cua* %s - after super().save_model: obj': %s", __name__, format(obj, 'detail'))


admin.site.register(CustomUser, CustomUserAdmin)
