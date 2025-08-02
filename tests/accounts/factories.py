from factory import Faker, django
from accounts import models
import pytest
from pytest_factoryboy import register

@register
class CustomUserFactory(django.DjangoModelFactory):
    '''Create a Custom User (Account)'''
    class Meta:
        model = models.CustomUser
    username = Faker('user_name') # see accounts/signals.py to override this.
    email = Faker('email')
    password=Faker('password')
    last_name=Faker('first_name')
    first_name=Faker('last_name')
    # deleted=None
