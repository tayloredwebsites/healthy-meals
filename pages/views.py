"""
Healthy Meals Web Site
Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals

pages/views.py - Views for the pages app.
"""

from django.views.generic import TemplateView


class HomePageView(TemplateView):
    """View for the home page."""
    template_name = "pages/home.html"


class AboutPageView(TemplateView):
    """View for the about page."""
    template_name = "pages/about.html"
