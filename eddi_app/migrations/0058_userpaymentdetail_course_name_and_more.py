# Generated by Django 4.0 on 2022-03-31 19:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0057_favouritecourse'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpaymentdetail',
            name='course_name',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Course name'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_image/', verbose_name='Profile Image'),
        ),
        migrations.CreateModel(
            name='CourseEnroll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date_time', models.DateTimeField(auto_now_add=True, verbose_name='Favourite Course Created Date Time')),
                ('payment_detail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.userpaymentdetail', verbose_name='Payment Detail')),
                ('user_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.userprofile', verbose_name='User Profile')),
            ],
        ),
    ]
