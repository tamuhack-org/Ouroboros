# Generated by Django 2.2.13 on 2023-12-03 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0018_auto_20231203_1708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='emergency_contact_email',
            field=models.CharField(max_length=255, verbose_name='Emergency Contact Email'),
        ),
        migrations.AlterField(
            model_name='application',
            name='emergency_contact_name',
            field=models.CharField(max_length=255, verbose_name='Emergency Contact Name'),
        ),
        migrations.AlterField(
            model_name='application',
            name='emergency_contact_phone',
            field=models.CharField(max_length=255, verbose_name='Emergency Contact Phone Number'),
        ),
        migrations.AlterField(
            model_name='application',
            name='emergency_contact_relationship',
            field=models.CharField(max_length=255, verbose_name='Emergency Contact Relationship'),
        ),
        migrations.AlterField(
            model_name='application',
            name='wares',
            field=models.CharField(max_length=255, verbose_name='Software or Hardware Track'),
        ),
    ]
