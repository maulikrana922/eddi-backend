# Generated by Django 3.1.7 on 2022-03-29 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0049_auto_20220329_0606'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nonbuiltinusertoken',
            name='email_id',
        ),
        migrations.AlterField(
            model_name='nonbuiltinusertoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auth_token', to='eddi_app.usersignup', verbose_name='email_id'),
        ),
    ]