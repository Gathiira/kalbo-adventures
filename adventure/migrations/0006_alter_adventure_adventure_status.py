# Generated by Django 3.2.7 on 2021-10-03 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0005_auto_20211003_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adventure',
            name='adventure_status',
            field=models.CharField(choices=[('ONGOING', 'ONGOING'), ('COMPLETE', 'COMPLETE'), ('CANCELLED', 'CANCELLED')], default='ONGOING', max_length=500),
        ),
    ]
