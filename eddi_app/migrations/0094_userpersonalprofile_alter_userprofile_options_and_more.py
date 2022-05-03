# Generated by Django 4.0 on 2022-05-03 09:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0093_contactuspagecms_section_2_latitude_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPersonalProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_image/', verbose_name='Profile Image')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Full Name')),
                ('location', models.CharField(blank=True, max_length=300, null=True, verbose_name='Location')),
                ('phone_number', models.BigIntegerField(blank=True, null=True, verbose_name='Phone Number')),
                ('email_id', models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='Email Id')),
            ],
            options={
                'verbose_name': 'User Personal Profile',
            },
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'User Eddi Profile'},
        ),
        migrations.AddField(
            model_name='supplierprofile',
            name='about_me',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='About Me'),
        ),
    ]
