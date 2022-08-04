# Generated by Django 4.0.3 on 2022-08-04 04:37

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0167_remove_invoicedata_uuid_remove_invoicedataevent_uuid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoicedata',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='UUID'),
        ),
        migrations.AddField(
            model_name='invoicedataevent',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='UUID'),
        ),
    ]
