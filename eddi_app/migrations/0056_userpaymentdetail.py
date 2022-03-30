# Generated by Django 4.0 on 2022-03-30 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0055_usersignup_is_authenticated'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPaymentDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_id', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email ID')),
                ('card_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='Card Type')),
                ('amount', models.FloatField(blank=True, null=True, verbose_name='Amount')),
                ('created_date_time', models.DateTimeField(auto_now_add=True, verbose_name='Payment Created Date Time')),
                ('status', models.CharField(blank=True, max_length=100, null=True, verbose_name='Payment Status')),
            ],
        ),
    ]