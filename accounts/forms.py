"""
Healthy Meals Web Site
Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals

accounts/forms.py - Forms for the accounts CustomUser admin app.
"""

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import CustomUser

logger = logging.getLogger(__name__)

class CustomUserCreationForm(AdminUserCreationForm): # pylint: disable=too-many-ancestors
    """A form for creating new users in the admin interface.

    Notes::

        - Should only be visible in the admin interface.
        - see: docs.djangoproject.com/en/6.0/topics/auth/customizing/#a-full-example

    """

    class Meta:
        """Meta class for CustomUserCreationForm."""
        model = get_user_model()  # CustomUser
        fields = (
            'email',
            'username',
            'password1',
            'password2',
        )

    def clean_email(self):
        """Validate that the email is unique."""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    model = CustomUser

    def clean_password2(self):
        """Validate that the two password entries match."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        # logger.debug('clean_password2 %s', self.cleaned_data["password1"])
        return password2

    def save(self, commit=True):
        """Save the provided password in hashed format."""
        user = super().save(commit=False)
        logger.debug('save super()')
        my_password2 = self.cleaned_data["password2"]
        user.set_password(my_password2)
        # logger.debug('#cua_cucf_s# set_password: %s',my_password2)
        if commit:
            logger.debug('save for commit integrity')
            user.save()
        logger.debug('admin.save')
        return user


class CustomUserChangeForm(UserChangeForm):
    """A form for updating CustomUsers in the admin interface."""
    class Meta:
        """Meta class for CustomUserChangeForm."""
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            # 'password',
            'first_name',
            'last_name',
            'is_superuser',
            'is_staff',
            # 'created_at',
            # 'created_by',
            # 'updated_at',
            # 'updated_by',
            # 'deleted',  # FieldError: it is a non-editable field and cannot be modified in the admin interface.
        )

        """.. todo:: research bug in django or django_allauth that prevents the CustomUser admin forms exclude statement from working.

        .. code-block:: python

            exclude = (
                # 'is_active',  # KeyError: "Key 'is_active' not found in 'CustomUserForm'. Choices are: email, first_name, is_staff, is_superuser, last_login, last_name, password, username."
                # 'is_staff',  # KeyError: "Key 'is_staff' not found in 'CustomUserForm'. Choices are: email, first_name, is_active, is_superuser, last_login, last_name, password, username."
                # 'date_joined',  # KeyError: "Key 'date_joined' not found in 'CustomUserForm'. Choices are: email, first_name, groups, is_active, is_staff, is_superuser, last_login, last_name, password, user_permissions, username."
                # 'groups',  # KeyError: "Key 'groups' not found in 'CustomUserForm'. Choices are: email, first_name, is_active, is_staff, is_superuser, last_login, last_name, password, username."
                # 'user_permissions',  # KeyError: "Key 'user_permissions' not found in 'CustomUserForm'. Choices are: email, first_name, groups, is_active, is_staff, is_superuser, last_login, last_name, password, username."
                # 'usable_password_0',
            )
       """
