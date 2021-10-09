# Generated by Django 3.2.7 on 2021-10-07 15:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('adventure', '0007_auto_20211006_1342'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reference_number', models.CharField(max_length=5000, unique=True)),
                ('book_status', models.CharField(choices=[('UNPAID', 'UNPAID'), ('COMPLETE', 'COMPLETE'), ('CANCELLED', 'CANCELLED'), ('REJECTED', 'REJECTED')], max_length=5000)),
                ('name', models.CharField(max_length=5000, null=True)),
                ('phone_number', models.CharField(max_length=5000, null=True)),
                ('idnum', models.CharField(max_length=5000, null=True)),
                ('adult_participants', models.IntegerField(null=True)),
                ('child_participants', models.IntegerField(null=True)),
                ('is_cleared', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('adventure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='adventure.adventure')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_bookings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reference_number', models.CharField(max_length=5000, unique=True)),
                ('invoice_status', models.CharField(choices=[('PENDING', 'PENDING'), ('COMPLETE', 'COMPLETE'), ('CANCELLED', 'CANCELLED')], max_length=255)),
                ('amount', models.CharField(max_length=50, null=True)),
                ('expiry_date', models.DateTimeField(blank=True, null=True)),
                ('date_due', models.DateTimeField(blank=True, null=True)),
                ('allow_partial_payment', models.BooleanField(blank=True, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice', to='booking.booking')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.CharField(max_length=50, null=True)),
                ('transaction_num', models.CharField(max_length=255)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('channel_transaction_number', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('COMPLETE', 'COMPLETE'), ('CANCELLED', 'CANCELLED')], max_length=255)),
                ('payment_channel', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(blank=True, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='booking.invoice')),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
            },
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('invoice_type', models.CharField(max_length=255)),
                ('narration', models.TextField(max_length=500)),
                ('amount', models.CharField(max_length=50)),
                ('date_created', models.DateTimeField(blank=True, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice_items', to='booking.invoice')),
            ],
        ),
    ]
