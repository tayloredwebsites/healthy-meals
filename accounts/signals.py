# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
# from .models import CustomUser


# @receiver(pre_save, sender=CustomUser)
# def email_is_also_username(sender, instance, **kwargs):
#     '''Force the username field to be the same as the email field

#     Prevent duplication of email addresses in the CustomUser model at the database level.

#     - there could be duplicate emails in the database, thus leaving a potential issue with duplicate emails in the database
#     - We do not want duplicate emails in the database, because we are logging in by email address
#     - ``Warning``: do not use this CustomUser model if you wish to have usernames that are other than the user's email address
#     - see: https://docs.allauth.org/en/latest/
#     - see: https://docs.allauth.org/en/latest/account/configuration.html

#     .. todo::
#         - consider not using a pre_save signal decorator to force username field to be set to the records email field value for all CustomUser records
#             - https://django.wiki/guides/django-signals-complete-guide/
#             - https://www.vindevs.com/blog/how-to-get-the-current-user-in-a-django-model-p64/
#             - try using view, form, or model_view to pass curent user to model
#             - see: https://stackoverflow.com/questions/855816/auto-populating-created-by-field-with-django-admin-site#answer-855866
#             - see: https://www.w3tutorials.net/blog/django-how-to-get-current-user-in-admin-forms/
#             - consider using 

#     '''
#     print(f'*** accounts.signals.email_is_also_username called')
#     if instance.username != instance.email:
#         print(f"{instance.__class__.__name__} changed username from {instance.username} to {instance.email}")
#         instance.username = instance.email


# @receiver(post_save, sender=CustomUser)
# def default_creator_updator(sender, instance, **kwargs):
#     '''Ensure that the user created_by, and updated_by fields are set to the initial super user if not set'''
#     # if created_by and updated_by fields are set, done
#     # get first superuser in database - hopefully id 1
#     # determine if this is an update or create ???
#     # set the appropriate fields and save
