# Generated by Django 2.2.4 on 2019-09-28 22:03

from django.db import migrations, models
import multiselectfield.db.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rsvp',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('datetime_submitted', models.DateTimeField(auto_now_add=True)),
                ('dietary_restrictions', multiselectfield.db.fields.MultiSelectField(choices=[('Vg', 'Vegan'), ('V', 'Vegetarian'), ('H', 'Halal'), ('K', 'Kosher'), ('FA', 'Food Allergies')], max_length=2)),
                ('shirt_size', models.CharField(choices=[('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], max_length=3)),
                ('notes', models.TextField(max_length=500)),
            ],
        ),
    ]
