# Generated by Django 4.0 on 2022-05-18 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0108_whatsoneddicms_delete_maincoursecategorycms'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersignup',
            name='is_resetpassword',
            field=models.BooleanField(default=True, verbose_name='is_resetpassword'),
        ),
    ]