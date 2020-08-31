# Generated by Django 2.2.10 on 2020-08-09 19:34

import application.filesize_validation
import application.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_auto_20200808_2035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='resume',
            field=models.FileField(help_text='Companies will use this resume to offer interviews for internships and full-time positions.', upload_to=application.models.uuid_generator, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf']), application.filesize_validation.FileSizeValidator(max_filesize=1.0)], verbose_name='Upload your resume (PDF only)'),
        ),
    ]