# Generated by Django 3.1.7 on 2022-03-29 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0052_nonbuiltinusertoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nonbuiltinusertoken',
            name='user',
            field=models.CharField(max_length=255, unique=True, verbose_name='email_id'),
        ),
    ]
