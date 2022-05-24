# Generated by Django 4.0.3 on 2022-05-23 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0115_alter_coursematerial_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplierorganizationprofile',
            name='rejection',
        ),
        migrations.AddField(
            model_name='supplierorganizationprofile',
            name='rejection_count',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Rejection Count'),
        ),
    ]