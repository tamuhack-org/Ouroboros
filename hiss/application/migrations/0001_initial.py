# Generated by Django 2.2.10 on 2020-02-17 18:26

import application.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='Wave',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('num_days_to_rsvp', models.IntegerField()),
                ('is_walk_in_wave', models.BooleanField(default=False, verbose_name='Is this wave for walk-ins?')),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('datetime_submitted', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('P', 'Under Review'), ('R', 'Waitlisted'), ('A', 'Admitted'), ('C', 'Confirmed'), ('X', 'Declined'), ('I', 'Checked in'), ('E', 'Expired')], default='P', max_length=1)),
                ('first_name', models.CharField(max_length=255, verbose_name='first name')),
                ('last_name', models.CharField(max_length=255, verbose_name='last name')),
                ('extra_links', models.CharField(blank=True, max_length=200, verbose_name="Point us to anything you'd like us to look at while considering your application")),
                ('question1', models.TextField(max_length=500, verbose_name='Tell us your best programming joke')),
                ('question2', models.TextField(max_length=500, verbose_name="What is the one thing you'd build if you had unlimited resources?")),
                ('question3', models.TextField(max_length=500, verbose_name="What is a cool prize you'd like to win at TAMUhack?")),
                ('resume', models.FileField(help_text='Companies will use this resume to offer interviews for internships and full-time positions.', upload_to=application.models.uuid_generator, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])], verbose_name='Upload your resume (PDF only)')),
                ('major', models.CharField(max_length=255, verbose_name="What's your major?")),
                ('classification', models.CharField(choices=[('Fr', 'Freshman'), ('So', 'Sophomore'), ('Jr', 'Junior'), ('Sr', 'Senior'), ('Ma', "Master's Student"), ('PhD', 'PhD Student'), ('O', 'Other')], max_length=3, verbose_name='What classification are you?')),
                ('gender', models.CharField(choices=[('NA', 'Prefer not to answer'), ('M', 'Male'), ('F', 'Female'), ('NB', 'Non-binary'), ('X', 'Prefer to self-describe')], default='NA', max_length=2, verbose_name="What's your gender?")),
                ('gender_other', models.CharField(blank=True, max_length=255, null=True, verbose_name='Self-describe')),
                ('race', multiselectfield.db.fields.MultiSelectField(choices=[('AI', 'American Indian or Alaskan Native'), ('AS', 'Asian'), ('BL', 'Black or African-American'), ('HI', 'Hispanic or Latino'), ('NH', 'Native Hawaiian or other Pacific Islander'), ('WH', 'White'), ('NA', 'Prefer not to answer'), ('O', 'Prefer to self-describe')], max_length=41, verbose_name='What race(s) do you identify with?')),
                ('race_other', models.CharField(blank=True, max_length=255, null=True, verbose_name='Self-describe')),
                ('grad_year', models.IntegerField(choices=[(2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025)], verbose_name='What is your anticipated graduation year?')),
                ('num_hackathons_attended', models.CharField(choices=[('0', 'This will be my first!'), ('1-3', '1-3'), ('4-7', '4-7'), ('8-10', '8-10'), ('10+', '10+')], max_length=22, verbose_name='How many hackathons have you attended?')),
                ('agree_to_coc', models.BooleanField(choices=[(True, 'Agree')], default=None)),
                ('is_adult', models.BooleanField(choices=[(True, 'Agree')], default=None, help_text='Please note that freshmen under 18 must be accompanied by an adult or prove that they go to Texas A&M.', verbose_name='Please confirm you are 18 or older.')),
                ('shirt_size', models.CharField(choices=[('WXXS', "Women's XXS"), ('WXS', "Women's XS"), ('WS', "Women's S"), ('WM', "Women's M"), ('WL', "Women's L"), ('WXL', "Women's XL"), ('WXXL', "Women's XXL"), ('XXS', 'Unisex XXS'), ('XS', 'Unisex XS'), ('S', 'Unisex S'), ('M', 'Unisex M'), ('L', 'Unisex L'), ('XL', 'Unisex XL'), ('XXL', 'Unisex XXL')], max_length=4, verbose_name='What size shirt do you wear?')),
                ('transport_needed', models.CharField(choices=[('D', 'Driving'), ('B', 'TAMUhack Bus'), ('BUT', 'TAMUhack Bus - UT Austin'), ('BUTD', 'TAMUhack Bus - UT Dallas'), ('BUTA', 'TAMUhack Bus - UT Arlington'), ('BUTSA', 'TAMUhack Bus - UTSA'), ('BUTRGV', 'TAMUhack Bus - UTRGV'), ('OB', 'Other Bus (Greyhound, Megabus, etc.)'), ('F', 'Flying'), ('P', 'Public Transportation'), ('M', 'Walking/Biking')], max_length=11, verbose_name='How will you be getting to the event?')),
                ('travel_reimbursement', models.BooleanField(default=False, help_text='Travel reimbursement is only provided if you stay the whole time and submit a project.', verbose_name="I'd like to apply for travel reimbursement")),
                ('additional_accommodations', models.TextField(blank=True, max_length=500, verbose_name='Do you require any special accommodations at the event?')),
                ('dietary_restrictions', models.CharField(choices=[('None', None), ('Vegan', 'Vegan'), ('Vegetarian', 'Vegetarian'), ('Halal', 'Halal'), ('Kosher', 'Kosher'), ('Gluten-free', 'Gluten-free'), ('Food allergy', 'Food allergy'), ('Other', 'Other')], default='None', max_length=50, verbose_name='Do you have any dietary restrictions?')),
                ('confirmation_deadline', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, max_length=300, verbose_name='Anything else you would like us to know?')),
                ('school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='application.School', verbose_name='What school do you go to?')),
            ],
        ),
    ]
