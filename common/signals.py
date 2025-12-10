# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import CustomUser


# @receiver(post_save, sender=CustomUser)
# def default_creator_updator(sender, instance, **kwargs):
#     '''Ensure that the user created_by, and updated_by fields are set to the initial super user if not set'''
#     # if created_by and updated_by fields are set, done
#     # get first superuser in database - hopefully id 1
#     # determine if this is an update or create ???
#     # set the appropriate fields and save
