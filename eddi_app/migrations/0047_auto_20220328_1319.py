# Generated by Django 3.1.7 on 2022-03-28 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0046_auto_20220328_1317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursedetails',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.usersignup'),
        ),
    ]
