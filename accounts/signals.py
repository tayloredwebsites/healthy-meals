from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CustomUser


@receiver(pre_save, sender=CustomUser)
def email_is_also_username(sender, instance, **kwargs):
    '''Force the username field to be the same as the email field

    Prevent duplication of email addresses in the CustomUser model at the database level.

    - there could be duplicate emails in the database, thus leaving a potential issue with duplicate emails in the database
    - We do not want duplicate emails in the database, because we are logging in by email address
    - ``Warning``: do not use this CustomUser model if you wish to have usernames that are other than the user's email address
    - see: https://docs.allauth.org/en/latest/
    - see: https://docs.allauth.org/en/latest/account/configuration.html

    We are using a pre_save signal decorator
    to force username field to be set to the records email field value for all CustomUser records

    '''
    if instance.username != instance.email:
        print(f"{instance.__class__.__name__} changed username from {instance.username} to {instance.email}")
        instance.username = instance.email
