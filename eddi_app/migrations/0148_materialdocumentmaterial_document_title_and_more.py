# Generated by Django 4.0.3 on 2022-06-23 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0147_remove_paybyinvoice_event_name_paybyinvoice_course_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='materialdocumentmaterial',
            name='document_title',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Document Title'),
        ),
        migrations.AddField(
            model_name='materialvideomaterial',
            name='video_title',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Video Title'),
        ),
    ]
