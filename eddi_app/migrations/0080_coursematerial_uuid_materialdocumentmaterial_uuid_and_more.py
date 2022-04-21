# Generated by Django 4.0 on 2022-04-20 06:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0079_coursedetails_meeting_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursematerial',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AddField(
            model_name='materialdocumentmaterial',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AddField(
            model_name='materialvideomaterial',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]