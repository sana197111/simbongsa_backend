# model.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Organization(models.Model):
    company_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    company_number = models.CharField(max_length=25, null=True)

class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    contact = models.CharField(max_length=25)
    company = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)

class VolunteerEvent(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    location = models.CharField(max_length=255, null=True)
    mbti_type = models.CharField(max_length=25, null=True)
    vol_start = models.DateTimeField()
    vol_end = models.DateTimeField()
    apply_start = models.DateTimeField()
    apply_end = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

class Participation(models.Model):
    participation_id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    apply_date = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(VolunteerEvent, on_delete=models.CASCADE)
