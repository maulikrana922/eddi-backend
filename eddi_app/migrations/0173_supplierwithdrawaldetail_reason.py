# Generated by Django 4.0.3 on 2022-08-30 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0172_supplierwithdrawaldetail'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplierwithdrawaldetail',
            name='reason',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Reason'),
        ),
    ]