from django.db import models

# Create your models here.

class Hacker(models.Model):
    first_name = charField(max_length=100)
    last_name = charField(max_length=100)
    # ...

    def __str__(self):
        return self.last_name

class HackerProfile(models.Model):
    major = charField(max_length=100)
    # ...