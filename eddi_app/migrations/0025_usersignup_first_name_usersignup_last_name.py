# Generated by Django 4.0.3 on 2022-03-21 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0024_auto_20220319_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersignup',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='First Name'),
        ),
        migrations.AddField(
            model_name='usersignup',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Last Name'),
        ),
    ]
