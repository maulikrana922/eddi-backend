# Generated by Django 4.0.3 on 2022-08-03 13:50

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0165_alter_coursedetails_author_bio'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlatformFeeCMS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_fee', models.IntegerField(blank=True, null=True, verbose_name='Platform Fee Value Percentage')),
                ('created_date_time', models.DateTimeField(auto_now_add=True, verbose_name='Created Date Time')),
            ],
            options={
                'verbose_name_plural': 'Platform Fee Table',
            },
        ),
        migrations.RemoveField(
            model_name='paybyinvoice',
            name='invoice_address',
        ),
        migrations.RemoveField(
            model_name='paybyinvoice',
            name='organization_reference',
        ),
        migrations.AddField(
            model_name='eventadpaymentdetail',
            name='invoice',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.invoicedataevent'),
        ),
        migrations.AddField(
            model_name='invoicedata',
            name='invoice_pdf',
            field=models.FileField(blank=True, null=True, upload_to='invoice/', verbose_name='Invoice Pdf'),
        ),
        migrations.AddField(
            model_name='invoicedata',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='UUID'),
        ),
        migrations.AddField(
            model_name='invoicedataevent',
            name='invoice_pdf',
            field=models.FileField(blank=True, null=True, upload_to='invoice/', verbose_name='Invoice Pdf'),
        ),
        migrations.AddField(
            model_name='invoicedataevent',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='UUID'),
        ),
        migrations.AddField(
            model_name='userpaymentdetail',
            name='invoice',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.invoicedata'),
        ),
        migrations.AddField(
            model_name='supplieraccountdetail',
            name='commission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='eddi_app.platformfeecms', verbose_name='Commission'),
        ),
    ]
