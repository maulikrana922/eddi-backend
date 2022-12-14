# Generated by Django 4.0 on 2022-05-05 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0094_userpersonalprofile_alter_userprofile_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoicedata',
            name='invoice_file',
        ),
        migrations.RemoveField(
            model_name='invoicedataevent',
            name='invoice_file',
        ),
        migrations.AddField(
            model_name='invoicedata',
            name='user_address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='User Address'),
        ),
        migrations.AddField(
            model_name='invoicedata',
            name='vat_charges',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Vat'),
        ),
        migrations.AddField(
            model_name='invoicedataevent',
            name='user_address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='User Address'),
        ),
        migrations.AddField(
            model_name='invoicedataevent',
            name='vat_charges',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Vat'),
        ),
    ]
