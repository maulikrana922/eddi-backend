# Generated by Django 4.0 on 2022-04-06 12:06

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0062_rename_event_eventad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventad',
            name='event_description',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Event Description'),
        ),
        migrations.AlterField(
            model_name='eventad',
            name='event_small_description',
            field=ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Event Small Description'),
        ),
    ]
