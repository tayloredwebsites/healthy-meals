# """
# Healthy Meals Web Site
# Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
# Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

# https://github.com/tayloredwebsites/healthy-meals

# accounts/views.py - Views for the accounts CustomUser admin app.
# """

# from allauth.account.views import PasswordChangeView
# from django.views.generic import ListView
# from django.views.generic.edit import CreateView, UpdateView  # , DeleteView
# from .models import CustomUser


# # from django.http import HttpResponseRedirect
# # from django.shortcuts import render

# class CustomUserCreateView(CreateView):
#     """ CreateView for CustomUser model. """
#     model = CustomUser
#     template_name = 'custom_user_form.html'

#     # success_url = reverse_lazy('custom_user_list')

#     # override form_valid to insert requesting user in the created_by, and the updated_by fields.
#     def form_valid(self, form):
#         """attach currently logged in user as created_by, and updated_by"""
#         form.instance.created_by = self.request.user
#         form.instance.updated_by = self.request.user
#         return super().form_valid(form)


# class CustomUserUpdateView(UpdateView):
#     """ UpdateView for CustomUser model. """
#     model = CustomUser
#     template_name = 'custom_user_form.html'

#     # success_url = reverse_lazy('custom_user_list')

#     # override form_valid to insert requesting user in the created_by, and the updated_by fields.
#     def form_valid(self, form):
#         """attach currently logged in user as created_by, and updated_by"""
#         form.instance.created_by = self.request.user
#         form.instance.updated_by = self.request.user
#         return super().form_valid(form)


# class CustomUserListView(ListView):
#     """ ListView for CustomUser model. """
#     model = CustomUser
#     template_name = 'custom_users.html'

#     def get_queryset(self):
#         """Override the get_queryset method to only allow superusers see all users."""
#         user = self.request.user
#         if user.is_superuser:
#             return CustomUser.objects.all()
#         return CustomUser.objects.filter(created_by=user)


# class HomeAfterPasswordChangeView(PasswordChangeView):
#     """ View to redirect to home page after password change. """
#     @property
#     def success_url(self):
#         """Redirect to home page after password change."""
#         return '/'


# home_after_password_change = HomeAfterPasswordChangeView.as_view()


# class PasswordChangeDoneView(PasswordChangeView):
#     """ View to redirect to home page after password change. """
