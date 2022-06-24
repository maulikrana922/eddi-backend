# Generated by Django 4.0.3 on 2022-06-22 06:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0146_paybyinvoice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paybyinvoice',
            name='event_name',
        ),
        migrations.AddField(
            model_name='paybyinvoice',
            name='course',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.coursedetails', verbose_name='Course'),
        ),
        migrations.AddField(
            model_name='paybyinvoice',
            name='product_name',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Product Name'),
        ),
        migrations.AddField(
            model_name='paybyinvoice',
            name='product_type',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Product Type'),
        ),
    ]