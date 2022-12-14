# Generated by Django 3.1.7 on 2022-03-17 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0021_remove_contactuspagecms_section_2_button_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactFormLead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(blank=True, max_length=100, null=True, verbose_name='Full Name')),
                ('email_id', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email ID')),
                ('phone_number', models.IntegerField(blank=True, max_length=100, null=True, verbose_name='Phone Number')),
                ('message', models.TextField(blank=True, max_length=500, null=True, verbose_name='Message')),
            ],
        ),
    ]
