import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from authentication.managers import UserManager

USER_AVAILABILITY_STATUS = [
    ("AVAILABLE", 'AVAILABLE'),
    ("NOT_AVAILABLE", 'NOT_AVAILABLE'),
]

ACCOUNT_DEFAULT_STATUS = [
    ("ACTIVE", "ACTIVE"),
    ("DEACTIVATED", "DEACTIVATED"),
    ("SUSPENDED", "SUSPENDED"),
]

USERTYPE = [
    ("PUBLICUSER", "PUBLICUSER"),
    ("STAFF", "STAFF"),
    ("ADMIN", "ADMIN"),
]


class UserCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    user_mapping = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class UserGroup(models.Model):
    group = models.OneToOneField(
        "auth.Group", unique=True, on_delete=models.CASCADE, )
    user_category = models.ForeignKey(UserCategory, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "{}".format(self.group.name)


class UserCategoryType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        UserCategory,
        on_delete=models.CASCADE,
        related_name="user_category_type",
        blank=True,
        null=True,
    )
    model_name = models.CharField(max_length=100, null=True, blank=True)
    serializer = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=250, null=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    usertype = models.ForeignKey(UserCategoryType, on_delete=models.CASCADE, blank=True, null=True)
    profile_photo = models.CharField(max_length=255, null=True, blank=True)
    enable_phone_notification = models.BooleanField(null=True, blank=True)
    enable_email_notification = models.BooleanField(null=True, blank=True)
    primary_role = models.CharField(max_length=255, null=True, blank=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    account_status = models.CharField(max_length=255, choices=ACCOUNT_DEFAULT_STATUS, default='ACTIVE')

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return str(self.email)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True