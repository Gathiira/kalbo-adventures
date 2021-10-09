import uuid

from django.db import models

from adventure import models as adv_models
from authentication import models as auth_models

BOOK_STATTUS = [
    ('UNPAID', 'UNPAID'),
    ('COMPLETE', 'COMPLETE'),
    ('CANCELLED', 'CANCELLED'),
    ('REJECTED', 'REJECTED'),
]

INVOICE_STATTUS = [
    ('PENDING', 'PENDING'),
    ('COMPLETE', 'COMPLETE'),
    ('CANCELLED', 'CANCELLED')
]


class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(auth_models.User, on_delete=models.CASCADE,
                             related_name='user_bookings', null=True)
    adventure = models.ForeignKey(adv_models.Adventure, on_delete=models.CASCADE, related_name='bookings')
    reference_number = models.CharField(max_length=5000, unique=True)
    book_status = models.CharField(max_length=5000, choices=BOOK_STATTUS)
    name = models.CharField(max_length=5000, null=True)
    phone_number = models.CharField(max_length=5000, null=True)
    idnum = models.CharField(max_length=5000, null=True)
    adult_participants = models.IntegerField(null=True)
    child_participants = models.IntegerField(null=True)
    is_cleared = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.reference_number)


#     to be implemented later
class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='invoice')
    reference_number = models.CharField(max_length=5000, unique=True)
    invoice_status = models.CharField(choices=INVOICE_STATTUS, max_length=255)
    amount = models.CharField(max_length=50, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    date_due = models.DateTimeField(blank=True, null=True)
    allow_partial_payment = models.BooleanField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.reference_number)


class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='invoice_items')
    invoice_type = models.CharField(max_length=255)
    narration = models.TextField(max_length=500)
    amount = models.CharField(max_length=50)
    date_created = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.invoice.reference_number)


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.CharField(max_length=50, null=True)
    transaction_num = models.CharField(max_length=255, blank=False, null=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    channel_transaction_number = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(choices=INVOICE_STATTUS, max_length=255)
    payment_channel = models.CharField(max_length=255, blank=False, null=False)
    date_created = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return str(self.transaction_num)