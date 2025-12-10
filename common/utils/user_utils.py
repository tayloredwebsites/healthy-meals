from pprint import pprint
from typing import List, Optional

from accounts.models import CustomUser
from allauth.account.models import EmailAddress

# def validate_email(email: str):
#     user: CustomUser = CustomUser.objects.get(email=email)
#     email_obj: CustomEmailAddress = CustomEmailAddress.objects.get_for_user(user, email)
#     email_obj.verified = True
#     email_obj.save()
#     return user

def get_or_create_superuser(**kwargs):
    pass

def get_or_create_custom_user(**kwargs):
    pass
    # """ add or create superuser with ID 1 & return user_info dict
    #
    # When fixture is called, it will:
    #     - find the superuser with an ID of 1, or else create a new superuser.
    #         -  note: this is required because accounts.CustomUser has created_by, and updated_by fields that default to ID 1 of the site superuser
    #
    # Notes:
    #     - https://pytest.org/en/latest/how-to/fixtures.html#request-context
    #     - https://pytest.org/en/latest/how-to/unittest.html
    #     - does this extend the pytext client?
    #     - does this reset the id values see django_db reset_sequences
    #         - thus superuser id may not be set to 1 in tests always
    #
    # Args:
    #     - request: the [pytest requesting test context](https://pytest.org/en/latest/how-to/fixtures.html#request-context)
    #         - request.cls: the testing test context class (UnitTest Class calling this)
    #
    # Returns:
    #     - the user_info dict, which includes:
    #         - the superuser at id = 1, or a newly created superuser @ id = 1
    #         - the username, email, and password, to be able to log in the user
    # """

    # errors: List[str] = []
    # user: Optional[CustomUser] = None
    # ret_dict: dict[str, CustomUser | None | dict] = {}
    #
    # print(f'*** {__name__} - get_or_create_custom_user - started')
    # print(f'*** {__name__} - get_or_create_custom_user - kwargs: {kwargs}')
    # all_field_names = [field.name for field in CustomUser._meta.get_fields()]
    # print(f'*** {__name__} - get_or_create_custom_user - all_field_names: {all_field_names}')
    # valid_field_names = ['id', 'email', 'first_name', 'last_name', 'password', 'is_superuser', 'is_staff', 'is_active', 'is_validated']
    # user_dict = {k: kwargs[k] for k in valid_field_names if k in kwargs}
    # pprint(f'*** {__name__} - get_or_create_custom_user - user_dict: {user_dict}')
    # if user_dict['email']:
    #     user_dict['email'] = user_dict['username']
    #     ret_dict['info'] = user_dict
    #     try:
    #         ret_dict['user'] = CustomUser.objects.get(email=user_dict['email'])
    #         if ret_dict['user'] is None:
    #             ret_dict['user'] = CustomUser.objects.create(**user_dict)
    #     return {'user_dict': user_dict, 'errors': ['Missing email'], 'user': None}
    # else:
    #     errors.append('Missing email')
    #     user

    # initial_count = CustomUser.objects.count()
    # if initial_count > 0:
    #     user = CustomUser.objects.get(user_info)
    #     pprint(f'*** {__name__} - found user: {user:detail}')
    #     user_info['user'] = user
    #     user_info['info'] = user_info
    # else:
    #     sup = CustomUser.objects.create(
    #         username=USERNAME,
    #         email=EMAIL,
    #         password=PASSWORD,
    #         is_superuser=True,
    #     )
    #     # # cannot create user with created_by, or updated_by to self, as self does not exist in the database yet.
    #     # sup.created_by = sup
    #     # sup.updated_by = sup
    #     sup.save()
    #     print(f'*** {__name__} - save() got CustomUser.objects.count(): {CustomUser.objects.count()}')
    #     print(f'*** {__name__} - Createdfirst superuser: {sup:detail}')
    #
    #     user_info['user'] = sup
    #     user_info['id'] = sup.id
    # return user_info
