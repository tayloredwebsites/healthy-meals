from django.conf import settings
from django.contrib import admin
from django.urls import path, include

# from accounts.views import HomeAfterPasswordChangeView
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
