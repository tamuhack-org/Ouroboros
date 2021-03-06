# Generated by Django 2.2.10 on 2020-08-09 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application", "0005_auto_20200413_1240"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="dietary_restrictions",
            field=models.ManyToManyField(
                blank=True, to="application.DietaryRestriction"
            ),
        ),
        migrations.AlterField(
            model_name="application",
            name="question3",
            field=models.TextField(
                max_length=500,
                verbose_name="What is a cool prize you'd like to win at Howdy Hack?",
            ),
        ),
        migrations.AlterField(
            model_name="application",
            name="transport_needed",
            field=models.CharField(
                choices=[
                    ("D", "Driving"),
                    ("B", "Howdy Hack Bus"),
                    ("BUT", "Howdy Hack Bus - UT Austin"),
                    ("BUTD", "Howdy Hack Bus - UT Dallas"),
                    ("BUTA", "Howdy Hack Bus - UT Arlington"),
                    ("BUTSA", "Howdy Hack Bus - UTSA"),
                    ("BUTRGV", "Howdy Hack Bus - UTRGV"),
                    ("OB", "Other Bus (Greyhound, Megabus, etc.)"),
                    ("F", "Flying"),
                    ("P", "Public Transportation"),
                    ("M", "Walking/Biking"),
                ],
                max_length=11,
                verbose_name="How will you be getting to the event?",
            ),
        ),
        migrations.AlterField(
            model_name="application",
            name="grad_year",
            field=models.IntegerField(
                choices=[
                    (2020, 2020),
                    (2021, 2021),
                    (2022, 2022),
                    (2023, 2023),
                    (2024, 2024),
                    (2025, 2025),
                ],
                verbose_name="What is your anticipated graduation year?",
            ),
        ),
    ]
