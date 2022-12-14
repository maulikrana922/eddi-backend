# Generated by Django 4.0.3 on 2022-05-26 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0120_usersignup_is_approved'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='homepagecms_sv',
            options={'verbose_name': 'Home Page SV'},
        ),
        migrations.AlterField(
            model_name='homepagecms_sv',
            name='section_1_image',
            field=models.ManyToManyField(blank=True, null=True, to='eddi_app.homepagecmsbanner_sv', verbose_name='Banner Image'),
        ),
        migrations.AlterField(
            model_name='homepagecms_sv',
            name='section_4_logo',
            field=models.ManyToManyField(blank=True, null=True, to='eddi_app.homepagecmspartners_sv', verbose_name='Partner Logo'),
        ),
        migrations.AlterField(
            model_name='homepagecms_sv',
            name='section_5_blog',
            field=models.ManyToManyField(blank=True, null=True, to='eddi_app.blogdetails_sv', verbose_name='Blog'),
        ),
        migrations.AlterField(
            model_name='homepagecms_sv',
            name='section_6_testinomials',
            field=models.ManyToManyField(blank=True, null=True, to='eddi_app.testinomialsdetails_sv', verbose_name='Testinomials'),
        ),
    ]
