# Generated by Django 2.2.13 on 2024-06-27 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0021_auto_20240620_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='major',
            field=models.CharField(choices=[('Computer Science', 'Computer Science'), ('Software Engineering', 'Software Engineering'), ('Computer Engineering', 'Computer Engineering'), ('Electrical Engineering', 'Electrical Engineering'), ('Information Technology', 'Information Technology'), ('Data Science', 'Data Science'), ('Other', 'Other')], default='NA', max_length=100, verbose_name="What's your major?"),
        ),
    ]
