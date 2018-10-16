from django.db import models

# Create your models here.

class Hacker(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # ...

    def __str__(self):
        return self.last_name

class HackerProfile(models.Model):
    major = models.CharField(max_length=100)
    OPTIONS = (
    	('M', 'male'),
    	('F', 'female'), 
    	('NB', 'non-binary'),
    	('NA', 'prefer to not disclose'),
    )
    gender = models.CharField(max_length= 2, choices = OPTIONS)

current_year = 2018

    GRAD_YEAR_CHOICES = [current_year, current_year +1, current_year +2, current_year+3, current_year+4, current_year+5]

    grad_year = models.CharField(max_length=4, choices = GRAD_YEAR_CHOICES)

    date_submitted = models.DateField()

