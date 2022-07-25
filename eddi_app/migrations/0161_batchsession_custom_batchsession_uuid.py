# Generated by Django 4.0.3 on 2022-07-25 07:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0160_rename_created_datetime_batchsession_created_date_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchsession',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True, verbose_name='UUID'),
        ),
    ]
