# Generated by Django 3.1.7 on 2022-03-25 07:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0030_auto_20220323_0551'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='First Name')),
                ('last_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Last Name')),
                ('gender', models.CharField(blank=True, max_length=50, null=True, verbose_name='Gender')),
                ('dob', models.CharField(blank=True, max_length=50, null=True, verbose_name='Date of Birth')),
                ('personal_number', models.IntegerField(blank=True, null=True, verbose_name='Personal Number')),
                ('phone_number', models.BigIntegerField(blank=True, null=True, verbose_name='Phone Number')),
                ('highest_education', models.CharField(blank=True, max_length=50, null=True, verbose_name='Highest Level of Education')),
                ('university_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='University Name')),
                ('highest_degree', models.CharField(blank=True, max_length=50, null=True, verbose_name='Highest Degree')),
                ('educational_area', models.CharField(blank=True, max_length=50, null=True, verbose_name='Educational Area')),
                ('other_education', models.CharField(blank=True, max_length=50, null=True, verbose_name='Other Relavant Education')),
                ('diplomas_certificates', models.CharField(blank=True, max_length=50, null=True, verbose_name='Diplomas and Certificates')),
                ('current_professional_role', models.CharField(blank=True, max_length=50, null=True, verbose_name='Current Professional Role')),
                ('additional_role', models.CharField(blank=True, max_length=50, null=True, verbose_name='Additional Role')),
                ('extra_curricular', models.CharField(blank=True, max_length=100, null=True, verbose_name='Extra Curricular You Want')),
                ('extra_curricular_competence', models.CharField(blank=True, max_length=100, null=True, verbose_name='Extra Curricular Competence You Have')),
                ('core_responsibilities', models.CharField(blank=True, max_length=100, null=True, verbose_name='Core Responsibilities')),
                ('level_of_role', models.CharField(blank=True, max_length=100, null=True, verbose_name='Level Of Role')),
                ('future_professional_role', models.CharField(blank=True, max_length=100, null=True, verbose_name='Future Professional Role')),
                ('course_category', models.CharField(blank=True, max_length=100, null=True, verbose_name='Course Categories')),
                ('area_of_interest', models.CharField(blank=True, max_length=100, null=True, verbose_name='Area of Interest')),
                ('agree_ads_terms', models.BooleanField(default=True)),
                ('created_date_time', models.DateTimeField(auto_now_add=True, verbose_name='Created Date Time')),
                ('modified_date_time', models.DateTimeField(auto_now_add=True, verbose_name='Modified Date Time')),
                ('email_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.usersignup')),
            ],
            options={
                'verbose_name': 'User Profile Table',
            },
        ),
    ]
