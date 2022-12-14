# Generated by Django 3.1.7 on 2022-03-07 13:14

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='utl_status',
            options={'verbose_name': 'Status Table'},
        ),
        migrations.AddField(
            model_name='coursedetails',
            name='supplier',
            field=models.ForeignKey(default=1, limit_choices_to={'is_supplier': True}, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.usersignup'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='coursecategorydetails',
            name='category_image',
            field=models.FileField(blank=True, null=True, upload_to='category_image/', verbose_name='Category Image'),
        ),
        migrations.AlterField(
            model_name='coursecategorydetails',
            name='category_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Category Name'),
        ),
        migrations.AlterField(
            model_name='coursecategorydetails',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.utl_status', verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='coursecategorydetails',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='additional_information',
            field=models.TextField(blank=True, max_length=1500, null=True, verbose_name='Additional Information'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='course_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.coursecategorydetails', verbose_name='Course Category'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='course_image',
            field=models.FileField(blank=True, null=True, upload_to='course_image/', verbose_name='Course Image'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='course_length',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Course Length'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='course_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.courselevel', verbose_name='Course Level'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='course_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Course Name'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='course_price',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Course Price'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='course_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.coursetype', verbose_name='Course Type'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='fee_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.feetype', verbose_name='Fee Type'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.utl_status', verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='coursedetails',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='courselevel',
            name='level_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Course Level Name'),
        ),
        migrations.AlterField(
            model_name='courselevel',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.utl_status', verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='courselevel',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='coursetype',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.utl_status', verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='coursetype',
            name='type_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Course Type Name'),
        ),
        migrations.AlterField(
            model_name='coursetype',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='feetype',
            name='fee_type_name',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Fee Type Name'),
        ),
        migrations.AlterField(
            model_name='feetype',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.utl_status', verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='feetype',
            name='uuid',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True, verbose_name='UUID'),
        ),
        migrations.AlterField(
            model_name='usersignup',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.utl_status', verbose_name='Status'),
        ),
    ]
