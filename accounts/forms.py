from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django import forms

from .models import CustomUser


class CustomUserCreationForm(AdminUserCreationForm):
    """form to create a new user (visible in admin interface)"""
    # usable_password = forms.CharField(widget=forms.PasswordInput)
    usable_password = None

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "is_superuser",
            # "is_active",  # see Action dropdown (and Go button) in Healthy Meals Admin Custom Users listing page
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "is_superuser",
            # "is_active",  # see Action dropdown (and Go button) in Healthy Meals Admin Custom Users listing page
        )
