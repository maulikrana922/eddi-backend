# Generated by Django 4.0.3 on 2022-05-27 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0122_alter_contactformlead_phone_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfileCMS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_welcome', models.CharField(blank=True, max_length=255, null=True, verbose_name='User Welcome')),
                ('content', models.TextField(blank=True, max_length=5000, null=True, verbose_name='content')),
                ('button_1_text', models.CharField(blank=True, max_length=50, null=True, verbose_name='Button 1 Text')),
                ('button_2_text', models.CharField(blank=True, max_length=50, null=True, verbose_name='Button 2 Text')),
                ('button_3_text', models.CharField(blank=True, max_length=50, null=True, verbose_name='Button 3 Text')),
                ('button_4_text', models.CharField(blank=True, max_length=50, null=True, verbose_name='Button 4 Text')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfileCMS_SV',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_welcome', models.CharField(blank=True, max_length=255, null=True, verbose_name='User Welcome')),
                ('content', models.TextField(blank=True, max_length=5000, null=True, verbose_name='content')),
                ('button_1_text', models.CharField(blank=True, max_length=50, null=True, verbose_name='Button 1 Text')),
                ('button_2_text', models.CharField(blank=True, max_length=50, null=True, verbose_name='Button 2 Text')),
                ('button_3_text', models.CharField(blank=True, max_length=50, null=True, verbose_name='Button 3 Text')),
                ('button_4_text', models.CharField(blank=True, max_length=50, null=True, verbose_name='Button 4 Text')),
            ],
        ),
    ]
