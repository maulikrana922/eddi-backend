# Generated by Django 3.1.7 on 2022-03-28 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0041_auto_20220327_0708'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursedetails',
            name='course_checkout_link',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Checkout Link'),
        ),
    ]
