# Generated by Django 4.0.3 on 2022-07-19 07:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0154_alter_coursedetails_supplier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersignup',
            name='user_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usertype', to='eddi_app.usertype', verbose_name='User Type'),
        ),
    ]
