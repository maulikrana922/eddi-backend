# Generated by Django 4.0.3 on 2022-07-18 10:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0153_userdevicetoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursedetails',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplier', to='eddi_app.usersignup', verbose_name='supplier'),
        ),
        migrations.AlterField(
            model_name='userdevicetoken',
            name='user_type',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='device_token', to='eddi_app.usersignup', verbose_name='User Type'),
        ),
    ]
