# Generated by Django 2.2.13 on 2024-08-10 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0022_auto_20240627_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='wants_team',
            field=models.CharField(choices=[('Friend', 'From a friend'), ('Tabling', 'Tabling outside Zachry'), ('Howdy Week', 'From Howdy Week'), ('Yard Sign', 'Yard sign'), ('Social Media', 'Social media'), ('Student Orgs', 'Though another student org'), ('TH Organizer', 'From a TAMUhack organizer'), ('ENGR Newsletter', 'From the TAMU Engineering Newsletter'), ('MLH', 'Major League Hacking (MLH)'), ('Attended Before', "I've attended TAMUhack before")], max_length=16, verbose_name='How did you hear about TAMUhack?'),
        ),
    ]