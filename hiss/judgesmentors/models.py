from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

STATUS_INVITED = "I"      # Invited (interest email sent)
STATUS_CONFIRMED = "C"    # Confirmed (signed up)
STATUS_CHECKED_IN = "CI"  # Checked in at event
STATUS_DECLINED = "D"     # Declined invitation

STATUS_CHOICES = [
    (STATUS_INVITED, "Invited"),
    (STATUS_CONFIRMED, "Confirmed"),
    (STATUS_CHECKED_IN, "Checked In"),
    (STATUS_DECLINED, "Declined"),
]

TRACK_CHOICES = [
    ("SW", "Software"),
    ("HW", "Hardware"),
    ("AI", "AI/ML"),
    ("GENERAL", "General"),
]

TSHIRT_CHOICES = [
    ("XS", "XS"),
    ("S", "S"),
    ("M", "M"),
    ("L", "L"),
    ("XL", "XL"),
    ("XXL", "XXL"),
]


class Judge(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='judge_profile')
    
    
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    tshirt_size = models.CharField(max_length=5, choices=TSHIRT_CHOICES, default="M")
    is_faculty = models.BooleanField(default=False)
    track = models.CharField(max_length=10, choices=TRACK_CHOICES, default="SW")
    additional_info = models.TextField(blank=True)
    
    
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=STATUS_INVITED)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.user.email})"
    
    class Meta:
        verbose_name = "Judge"
        verbose_name_plural = "Judges"


class Mentor(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    
    
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    tshirt_size = models.CharField(max_length=5, choices=TSHIRT_CHOICES, default="M")
    is_tamu_faculty = models.BooleanField(default=False)
    track = models.CharField(max_length=10, choices=TRACK_CHOICES, default="SW")
    additional_info = models.TextField(blank=True)
    
    
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=STATUS_INVITED)
    
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.user.email})"
    
    class Meta:
        verbose_name = "Mentor"
        verbose_name_plural = "Mentors"