# Generated by Django 3.1.7 on 2022-03-22 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0027_auto_20220322_0413'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='privacypolicycms',
            name='section_1_image',
        ),
        migrations.AddField(
            model_name='privacypolicycms',
            name='section_1_image',
            field=models.ImageField(blank=True, null=True, upload_to='privacy_policy/', verbose_name='Banner Image'),
        ),
        migrations.RemoveField(
            model_name='termsconditioncms',
            name='section_1_image',
        ),
        migrations.AddField(
            model_name='termsconditioncms',
            name='section_1_image',
            field=models.ImageField(blank=True, null=True, upload_to='terms_conditon/', verbose_name='Banner Image'),
        ),
    ]
