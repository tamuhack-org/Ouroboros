# Generated by Django 2.2.13 on 2024-10-24 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0024_auto_20240823_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='major',
            field=models.CharField(choices=[('Computer Science', 'Computer Science'), ('Computer Engineering', 'Computer Engineering'), ('Computing', 'Computing'), ('Electrical Engineering', 'Electrical Engineering'), ('Management Information Systems', 'Management Information Systems'), ('Data Science/Engineering', 'Data Science/Engineering'), ('General Engineering', 'General Engineering'), ('Biomedical Engineering', 'Biomedical Engineering'), ('Chemical Engineering', 'Chemical Engineering'), ('Civil Engineering', 'Civil Engineering'), ('Industrial Engineering', 'Industrial Engineering'), ('Mechanical Engineering', 'Mechanical Engineering'), ('Aerospace Engineering', 'Aerospace Engineering'), ('Electronic Systems Engineering Technology (ESET)', 'Electronic Systems Engineering Technology (ESET)'), ('Mathematics', 'Mathematics'), ('Physics', 'Physics'), ('Statistics', 'Statistics'), ('Biology', 'Biology'), ('Chemistry', 'Chemistry'), ('Other', 'Other')], default='NA', max_length=100, verbose_name="What's your major?"),
        ),
        migrations.AlterField(
            model_name='application',
            name='wants_team',
            field=models.CharField(choices=[('Friend', 'From a friend'), ('Tabling', 'Tabling outside Zachry'), ('Howdy Week', 'From Howdy Week'), ('Yard Sign', 'Yard sign'), ('Social Media', 'Social media'), ('Student Orgs', 'Though another student org'), ('TH Organizer', 'From a TAMUhack organizer'), ('ENGR Newsletter', 'From the TAMU Engineering Newsletter'), ('MLH', 'Major League Hacking (MLH)'), ('Attended Before', "I've attended HowdyHack before")], max_length=16, verbose_name='How did you hear about HowdyHack?'),
        ),
        migrations.AlterField(
            model_name='application',
            name='wares',
            field=models.CharField(blank=True, choices=[('SW', 'Software'), ('HW', 'Hardware')], default='NA', max_length=8, verbose_name='TAMUhack will be partnering with IEEE to offer a dedicated hardware track and prizes. Participants can choose to compete in this track or in the general software tracks. Would you like to compete in the software or hardware track'),
        ),
    ]
