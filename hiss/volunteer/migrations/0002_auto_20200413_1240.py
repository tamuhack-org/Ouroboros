# Generated by Django 2.2.10 on 2020-04-13 17:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0005_auto_20200413_1240"),
        ("volunteer", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="foodevent",
            name="restrictions",
        ),
        migrations.AddField(
            model_name="foodevent",
            name="restrictions",
            field=models.ManyToManyField(to="application.DietaryRestriction"),
        ),
    ]
