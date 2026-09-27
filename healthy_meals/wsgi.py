"""
Healthy Meals Web Site
Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals

healthy_meals/wsgi.py - WSGI configuration for the healthy_meals app.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthy_meals.settings")

application = get_wsgi_application()
