"""
Healthy Meals Web Site
Copyright (C) 2026 David A. Taylor of Taylored Web Sites (tayloredwebsites.com)
Licensed under AGPL-3.0-only.  See https://opensource.org/license/agpl-v3/

https://github.com/tayloredwebsites/healthy-meals

accounts/helpers.py - Accounts helpers for CustomUser records
"""

import logging
from typing import Optional

from allauth.account.models import EmailAddress
from django.core.exceptions import ValidationError

from accounts.models import CustomUser

logger = logging.getLogger(__name__)

def is_user_valid(user_rec: CustomUser) -> tuple[bool, Optional[list[str]]]:
    """Is the user a valid CustomUser?

    Args:
        - The custom user record to be validated.

    Returns: a tuple: (
            is_valid: bool,  # True, or False
            errs: list[str],  # returns [] if no errors
        )

    Example:

    .. code-block:: python

        is_valid, errs = is_user_valid(user_rec)
        assert is_valid, '; '.join(errs)
    """
    errs: list[str] = []
    logger.debug('*cuh* %(name)s - is_user_valid - user_rec: %(user_rec)s', {'name': __name__, 'user_rec': user_rec})
    # validate the user
    try:
        logger.debug('*cuh* CustomUser record: %(user_rec)s is being validated', {'user_rec': format(user_rec, 'detail')})
        user_rec.full_clean()
        logger.debug('*cuh* user_rec is validated')
        return True, []
    except ValidationError as ex:
        errs.extend(get_invalid_record_errors(ex))
        return False, errs


def get_invalid_record_errors(exception: ValidationError) -> list[str]:
    """Utility function to extract the errors from a ValidationError

    Args:
        - The ValidationError exception to be extracted.

    Returns: a tuple: (
            is_valid: bool,  # True, or False
            errs: list[str],  # returns [] if no errors
        )

    Example:

    .. code-block:: python

        is_valid, errs = is_user_valid(user_rec)
        assert is_valid, '; '.join(errs)
    """
    errs: list[str] = []
    for field, errors in exception:
        # logger.debug(f'{field}: {errors}')
        if len(errors) > 0:
            for err in errors:
                logger.debug('%s', err)
                errs.append(f'{err} (in {field})')
    logger.debug(errs)
    return errs


def is_user_email_valid(email_str: str, user_rec: CustomUser = None) -> tuple[bool, Optional[list[str]], Optional[dict]]:
    """Has the email record for this CustomUser been created and validated?

    Returns:: a tuple: (
            is_valid: bool, # True, or False
            err_str: list[str], # returns [] if no errors
            recs_dict: dict, # returns {'CustomUser': user_rec, 'EmailAddress': email_rec} if no errors
        )

    Example::

    .. code-block:: python

        is_valid, errs, recs_dict = is_user_email_valid(user_rec)
        if not is_valid:
            is_valid, errs, recs_dict = validate_user_email(user_rec.email, user_rec, recs_dict.get('EmailAddress'))
        # if testing
        assert is_valid, errs
        # production code
        if not is_valid: raise ValueError(errs)
    """
    logger.debug('*cuh* %(name)s - is_user_email_valid: for %(email)s', {'name': __name__, 'email': email_str})
    try:
        if user_rec is None:
            user_rec = CustomUser.objects.get(email=email_str)
        else:
            if user_rec.email != email_str:
                raise ValueError(f'user_rec.email: {user_rec.email} does not match email_str: {email_str}')
        if user_rec is None:
            raise ValueError(f'ERROR, there is no user with the email: {email_str}')
        email_rec: EmailAddress = EmailAddress.objects.get_for_user(user_rec, email_str)
        logger.debug('*cuh* email address: %(email)s has email_rec: %(email_rec)s', {'email': email_str, 'email_rec': format(email_rec, 'detail')})
        return email_rec.verified, [], {'CustomUser': user_rec, 'EmailAddress': email_rec}
    except CustomUser.DoesNotExist:
        err = f'*cuh* CustomUser for email_str: {email_str} does not exist'
        # logger.debug(f'ERROR, {err}')
        return False, [err], {'CustomUser': None, 'EmailAddress': None}
    except EmailAddress.DoesNotExist:
        err = f'ERROR, EmailAddress record for CustomUser with email: {email_str} does not exist'
        # logger.debug(err)
        return False, [err], {'CustomUser': user_rec, 'EmailAddress': None}
    except Exception as ex:  # pylint: disable=W0718  # broad exception logged as error, and returned as an error
        err = f'ERROR, is_user_email_valid exception: {type(ex)} - {ex}'
        logger.error(err)
        return False, [err], {'CustomUser': None, 'EmailAddress': None}


# noinspection PyBroadException
def validate_user_email(email_str: str, user_rec: CustomUser = None, email_rec: EmailAddress = None) -> tuple[bool, Optional[list[str]], Optional[dict]]:
    """Ensure that the email record for this CustomUser (EmailAddress) been created and validated

    Returns:: a tuple: (
            is_valid: bool, # True, or False
            err_str: list[str], # returns [] if no errors
            recs_dict: dict, # returns {'CustomUser': user_rec, 'EmailAddress': email_rec} if no errors
        )

    Example::

    .. code-block:: python

    is_valid, errs, recs_dict = is_user_email_valid(user_rec)
    if not is_valid:
        is_valid, errs, recs_dict = validate_user_email(user_rec.email, user_rec, recs_dict.get('EmailAddress'))
    # if testing
    assert is_valid, errs
    # production code
    if not is_valid: raise ValueError(errs)
    """
    logger.debug('*cuh* %s - validate_user_email: for %s', __name__, email_str)
    try:
        if user_rec is None:
            # get the user_rec if it is not passed in
            user_rec = CustomUser.objects.get(email=email_str)
        else:
            # ensure that the user_rec passed in has the same email as the email_str
            if user_rec.email != email_str:
                raise ValueError(f'user_rec.email: {user_rec.email} does not match email_str: {email_str}')
        if user_rec is None:
            # there is no user with an email address of email_str
            raise ValueError(f'ERROR, there is no user with the email: {email_str}')
        if email_rec is None:
            # get the EmailAddress record for the user_rec if it is not passed in
            email_rec: EmailAddress = EmailAddress.objects.get_for_user(user_rec, email_str)
        else:
            if email_rec.user != user_rec or email_rec.email != email_str:
                raise ValueError(f'email_rec.user: {email_rec.user.id} does not match user_rec: {user_rec.id} or email_rec.email: {email_rec.email} does not match email_str: {email_str}')
        # Update the fields in the EmailAddress to make it valid
        if not email_rec.verified or not email_rec.primary:
            email_rec.verified = True
            email_rec.primary = True  # always true since email is the primary key.
            email_rec.save()
        return True, [], {'CustomUser': user_rec, 'EmailAddress': email_rec}
    except CustomUser.DoesNotExist as ex1:
        err = f'CustomUser for email_str: {email_str} does not exist'
        logger.error(f'ERROR: {err}')  # pylint: disable=W1203  # no lazy logging, it is a logger.error, and also used in the return statement
        return False, [ex1, err], {'CustomUser': None, 'EmailAddress': None}
    except EmailAddress.DoesNotExist:
        # Create the EmailAddress record for the CustomUser if it does not exist
        is_valid, errs, recs_dict = create_user_email(user_rec, email_str)
        return is_valid, errs, recs_dict
    except Exception as ex3:  # pylint: disable=W0718  # broad exception logged as error, and returned as an error
        err = f'ERROR, validate_user_email got Exception: {type(ex3)} - {ex3}'
        logger.error(err)
        return False, [err], {'CustomUser': None, 'EmailAddress': None}

def create_user_email(user_rec: CustomUser, email_str: str) -> tuple[bool, Optional[list[str]], Optional[dict]]:
    """Create an EmailAddress record for the CustomUser"""
    logger.debug('*cuh* %(name)s - create_user_email - create an EmailAddress record for email: %(email)s', {'name': __name__, 'email': email_str})
    try:
        email_rec = EmailAddress.objects.create(
            user=user_rec,
            email=email_str,
            verified=True,
            primary=True
        )
    except Exception as ex:  # pylint: disable=W0718  # broad exception logged as error, and returned as an error
        err = f'Exception creating EmailAddress: {type(ex)} - {ex}'
        logger.Error(err)
        return False, [err], {}
    return True, [], {'EmailAddress': email_rec}

# def get_or_create_custom_user(**kwargs):
#     """Create CustomUser by matching email address, or creating a new one
#
#     Notes::
#
#         - to get an existing user, pass email only (args section)
#         - do a return section
#         - This is needed because factoryboy does not create related EmailAddress record
#             - to be able to validate a CustomUser, it needs the attached EmailAddress
#         - This method will not confirm the email address
#             - see allauth.account.utils.create_user
#             - see allauth.account.utils.complete_signup
#         - Returns the new user, the info used to create it, and any errors.
#     """
#     # user = CustomUser.objects.get(email=email)
#     errors: List[str] = []
#     user: Optional[CustomUser] = None
#     recs_dict: dict[str, CustomUser | None | dict] = {}
#
#     logger.debug(f'*cuh* {__name__} - get_or_create_custom_user - started')
#     # logger.debug(f'*cuh* {__name__} - get_or_create_custom_user - kwargs: {kwargs}')
#     valid_field_names = ['id', 'email', 'first_name', 'last_name', 'password', 'is_superuser', 'is_staff', 'is_active']
#     user_dict = {k: kwargs[k] for k in valid_field_names if k in kwargs}
#     # plogger.debug(f'*cuh* {__name__} - get_or_create_custom_user user_dict:')
#     # plogger.debug(user_dict)
#     if user_dict.get('user'):
#         # we passed a user record, get it.
#         user = user_dict['user']
#         #### validate the user, refactoring the validation below
#         is_val, errs = is_user_valid(user)
#         errors.append(errs)
#         if not is_val:
#             errors.append(f'User is not valid')
#     elif user_dict['email']:
#         # we passed the email, which is required if not passing a user.
#         # make sure that we set the username to the email if we are creating it
#         user_dict['username'] = user_dict['email']
#         # load up the user info for return
#         try:
#             # first, try to find the user, and if so we are done
#             user = CustomUser.objects.get(email=user_dict['email'])
#             logger.debug('user exists')
#         except CustomUser.DoesNotExist:
#             # we did not find the user
#             if len(user_dict) == 2:
#                 # we found the user, since we only passed the email and username, we are done
#                 pass
#             else:
#                 user = create_custom_user(user_dict)
#     else:
#         errors.append('Missing required email field')
#     # return {'user_dict': user_dict, 'errors': errors, 'user': user}
#     return (user_dict, errors, user)
#
# def create_custom_user(user_dict: dict) -> CustomUser:
#     logger.debug('load up the values for the user to be validated and created:')
#     user = CustomUser(**user_dict)
#     logger.debug(f'{user: detail}')
#     is_val, errs = is_user_valid(user)
#     errors.append(errs)
#     if not is_val:
#         errors.append('User is not valid')
#     else:
#         # call the allauth-django's special set_password function
#         if user_dict.get('password'):
#             user.set_password(user_dict['password'])
#         else:
#             errors.append(f'no password provided')
#         logger.debug('user is valid')
#         # user.save()
#         # # probably useless code because user is already validated
#         # try to create the user
#         try:
#             user.save()
#             logger.debug(f'saved user: {user: detail}')
#             EmailAddress.objects.create(user=user, email=user_dict['email'])  # verified=True, primary=True)
#         except Exception as ex:  # pragma: no cover
#             # We should not ever get here because we already validated 'user'
#             ex_name = ex.__class__.__name__
#             logger.debug(f'*cuh* {__name__} - get_or_create_custom_user - save Exception: {ex_name} {ex}')
#             if ex_name == 'ValidationError':
#                 errors.extend(get_invalid_fields(ex))
#             else:
#                 raise ex
