# Generated by Django 3.1.7 on 2022-03-26 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0035_coursedetails_course_by_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursedetails',
            name='course_by_admin',
        ),
    ]