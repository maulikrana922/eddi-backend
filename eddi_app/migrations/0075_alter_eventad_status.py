# Generated by Django 4.0 on 2022-04-13 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0074_remove_eventadpaymentdetail_uuid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventad',
            name='status',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.utl_status', verbose_name='Status'),
        ),
    ]