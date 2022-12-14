# Generated by Django 4.0.3 on 2022-08-04 07:24

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0168_invoicedata_uuid_invoicedataevent_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paybyinvoice',
            name='email_id',
        ),
        migrations.AddField(
            model_name='paybyinvoice',
            name='invoice_email',
            field=models.EmailField(max_length=500, null=True, verbose_name='Invoice Email'),
        ),
        migrations.AddField(
            model_name='paybyinvoice',
            name='student_email',
            field=models.EmailField(max_length=500, null=True, verbose_name='Student Email'),
        ),
    ]
