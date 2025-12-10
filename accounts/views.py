"""
Healthy Meals Web Site
Copyright (C) 2025 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals - accounts/views.py
"""
from allauth.account.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView  # , DeleteView
from .models import CustomUser


# from django.http import HttpResponseRedirect
# from django.shortcuts import render

class CustomUserCreateView(CreateView):
    model = CustomUser
    template_name = 'custom_user_form.html'
    success_url = reverse_lazy('custom_user_list')

    # override form_valid to insert requesting user in the created_by, and the updated_by fields.
    def form_valid(self, form):
        # attach currently logged in user as created_by, and updated_by
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class CustomUserUpdateView(UpdateView):
    model = CustomUser
    template_name = 'custom_user_form.html'
    success_url = reverse_lazy('custom_user_list')

    # override form_valid to insert requesting user in the created_by, and the updated_by fields.
    def form_valid(self, form):
        # attach currently logged in user as created_by, and updated_by
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class CustomUserListView(ListView):
    model = CustomUser
    template_name = 'custom_users.html'

    # override the get_queryset method to only allow superusers see all users.
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CustomUser.objects.all()
        else:
            return CustomUser.objects.filter(created_by=user)

class HomeAfterPasswordChangeView(PasswordChangeView):
    @property
    def success_url(self):
        return '/'

home_after_password_change = HomeAfterPasswordChangeView.as_view()

class PasswordChangeDoneView(PasswordChangeView):
