# Generated by Django 3.2.7 on 2021-10-06 10:42

from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('adventure', '0006_alter_adventure_adventure_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=250)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='adventure',
            name='organizer',
            field=models.ManyToManyField(related_name='organizer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='adventure',
            name='payment_channel',
            field=models.ManyToManyField(blank=True, related_name='adventure', to='adventure.PaymentChannel'),
        ),
        migrations.AddField(
            model_name='adventure',
            name='category',
            field=models.ManyToManyField(related_name='category', to='adventure.Category'),
        ),
    ]
