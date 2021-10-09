import logging

from django.contrib.auth.models import Group
from django.db import transaction

from authentication import models as auth_models

log = logging.getLogger(__name__)


def register_user(payload):
    try:
        email = payload['email']
        users = auth_models.User.objects.filter(email=email, is_active=True)
        if not users.exists():
            with transaction.atomic():
                password = auth_models.User.objects.make_random_password()
                user = auth_models.User.objects.create_user(
                    password=password,
                    email=email,
                    is_staff=False
                )
                user.full_name = payload['full_name']
                user.phone_number = payload['phone_number']
                user.is_active = True
                user.enable_phone_notification = True
                user.enable_email_notification = True

                user_type = payload['user_type']
                if user_type:
                    try:
                        group_instance = Group.objects.get(name=user_type)
                    except Exception as e:
                        log.error(e)
                        transaction.set_rollback(True)
                        return False, "User type provided does not exists"
                    user.groups.add(group_instance)

                user.save()
        else:
            user = users.first()

        return True, user
    except Exception as e:
        log.error(e)
        return False, 'Failed to create user'