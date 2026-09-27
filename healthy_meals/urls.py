"""
Healthy Meals Web Site
Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals

healthy_meals/urls.py - URL configuration for the healthy_meals app.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Healthy Meals Admin'

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('accounts/password/change', HomeAfterPasswordChangeView.as_view(), name='account_password_change'),
    path("accounts/", include("allauth.urls")),
    path("", include("pages.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path("__debug__/", include(debug_toolbar.urls)),
                  ] + urlpatterns
