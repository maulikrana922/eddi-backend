# Generated by Django 4.0 on 2022-05-10 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0101_coursedetails_supplier_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursedetails',
            name='target_users',
            field=models.CharField(blank=True, max_length=10000, null=True, verbose_name='Target Users'),
        ),
    ]
