"""
Healthy Meals Web Site
Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals

healthy_meals/context_processors.py - Context processors for the healthy_meals app.
"""

from django.conf import settings


def testing_context(request):
    """Add TESTING context for use in templates to indicate when running in the testing environment

    Notes:
        - see: https://docs.djangoproject.com/en/2.0/_modules/django/template/context_processors/ (see def debug)
        - see: healthy_meals.settings.py - TEMPLATES "OPTIONS" "context_processors" references: "healthy_meals.context_processors.testing_context"
    """
    return {'TESTING': settings.TESTING}
