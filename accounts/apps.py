"""
Healthy Meals Web Site
Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals

accounts/apps.py - Accounts App (CustomUser records) Configuration
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Accounts App (CustomUser records) Configuration"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
