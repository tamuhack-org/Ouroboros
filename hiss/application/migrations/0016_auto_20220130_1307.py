# Generated by Django 2.2.13 on 2022-01-30 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application", "0015_auto_20201228_2150"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="additional_accommodations",
            field=models.TextField(
                blank=True,
                max_length=500,
                verbose_name="Do you require any special accommodations at the event? Please list all dietary restrictions here.",
            ),
        ),
        migrations.AlterField(
            model_name="application",
            name="grad_year",
            field=models.IntegerField(
                choices=[
                    (2022, 2022),
                    (2023, 2023),
                    (2024, 2024),
                    (2025, 2025),
                    (2026, 2026),
                ],
                verbose_name="What is your anticipated graduation year?",
            ),
        ),
        migrations.AlterField(
            model_name="application",
            name="question3",
            field=models.TextField(
                max_length=500,
                verbose_name="If given the choice, would you attend TAMUhack in-person or virtually? Note: In-person availability is only for the first 500 people who check-in at our venue on the morning of TAMUhack.",
            ),
        ),
    ]