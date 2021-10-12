import uuid

from django.db import models

from authentication import models as auth_models

ADVENTURE_STATUS = [
    ('ONGOING', 'ONGOING'),
    ('COMPLETE', 'COMPLETE'),
    ('CANCELLED', 'CANCELLED'),
]


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'


class PaymentChannel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250)
    account = models.CharField(max_length=250)
    is_bank = models.BooleanField(default=False)
    description = models.TextField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}  --- {self.account}  --- {self.is_bank}'


class Adventure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    reference_number = models.CharField(max_length=500, unique=True)
    adventure_status = models.CharField(
        max_length=500,
        choices=ADVENTURE_STATUS, default='ONGOING')
    created_by = models.CharField(max_length=250, null=True)
    description = models.TextField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    payment_channel = models.ManyToManyField(
        PaymentChannel, related_name='adventure', blank=True)
    category = models.ManyToManyField(
        Category, related_name='category')
    organizer = models.ManyToManyField(
        auth_models.User, related_name='organizer')
    slots = models.IntegerField()
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.reference_number} -- {self.title}'

class Inclusives(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE, related_name='inclusives')
    name = models.CharField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Price(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adventure = models.OneToOneField(Adventure, on_delete=models.CASCADE, related_name='prices')
    adult = models.IntegerField(null=True)
    child = models.IntegerField(null=True)
    discount = models.IntegerField(null=True)
    count = models.IntegerField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.adult} --- {self.child}'


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE, related_name='images')
    image_id = models.CharField(max_length=250)
    category = models.CharField(max_length=250, null=True)
    date_created = models.DateTimeField(auto_now_add=True)