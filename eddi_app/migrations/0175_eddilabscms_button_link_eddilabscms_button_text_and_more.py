# Generated by Django 4.0.3 on 2022-09-12 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0174_eddilabscms_eddilabscms_sv'),
    ]

    operations = [
        migrations.AddField(
            model_name='eddilabscms',
            name='button_link',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Button Link'),
        ),
        migrations.AddField(
            model_name='eddilabscms',
            name='button_text',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Button Text'),
        ),
        migrations.AddField(
            model_name='eddilabscms_sv',
            name='button_link',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Button Link'),
        ),
        migrations.AddField(
            model_name='eddilabscms_sv',
            name='button_text',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Button Text'),
        ),
    ]
