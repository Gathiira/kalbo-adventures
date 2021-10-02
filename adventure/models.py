import uuid

from django.db import models


# Create your models here.
class PaymentChannel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250)
    account = models.CharField(max_length=250)
    is_bank = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)


class Adventure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    description = models.TextField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    payment_channel = models.ForeignKey(
        PaymentChannel,
        on_delete=models.DO_NOTHING,
        related_name='adventure')
    slots = models.IntegerField()
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)


class Inclusives(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE, related_name='inclusives')
    name = models.CharField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True)


class Price(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adventure = models.OneToOneField(Adventure, on_delete=models.CASCADE, related_name='prices')
    adult = models.IntegerField()
    child = models.IntegerField()
    discount = models.IntegerField()
    count = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adventure = models.ForeignKey(Adventure, on_delete=models.CASCADE, related_name='images')
    image_id = models.CharField(max_length=250)
    category = models.CharField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)