# Generated by Django 2.2.3 on 2019-07-23 03:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VolunteerApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('grad_year', models.CharField(choices=[(None, '-- Select Option --'), ('Fall 2019', 'Fall 2019'), ('Spring 2020', 'Spring 2020'), ('Fall 2020', 'Fall 2020'), ('Spring 2021', 'Spring 2021'), ('Fall 2021', 'Fall 2021'), ('Spring 2022', 'Spring 2022'), ('Fall 2022', 'Fall 2022'), ('Spring 2023', 'Spring 2023'), ('Other', 'Other')], max_length=11, verbose_name='What is your anticipated graduation date?')),
                ('shirt_size', models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], default=None, max_length=3, verbose_name='Shirt size?')),
                ('engr_honors', models.BooleanField(default=False, verbose_name='Do you need to receive Engineering Honors credit?')),
            ],
        ),
        migrations.CreateModel(
            name='WorkshopEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('hacker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('volunteers', models.ManyToManyField(related_name='registered_shifts', to='volunteer.VolunteerApplication')),
            ],
        ),
        migrations.CreateModel(
            name='FoodEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('meal', models.CharField(choices=[('Breakfast', 'Breakfast'), ('Lunch', 'Lunch'), ('Dinner', 'Dinner'), ('Midnight Snack', 'Midnight Snack')], max_length=14)),
                ('restrictions', models.CharField(choices=[('Vegan', 'Vegan'), ('Vegetarian', 'Vegetarian'), ('Halal', 'Halal'), ('Kosher', 'Kosher'), ('Food Allergies', 'Food Allergies')], max_length=14)),
                ('hacker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
