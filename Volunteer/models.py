# model.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Organization(models.Model):
    organization_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    contact = models.CharField(max_length=15)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)

class VolunteerEvent(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True)
    location = models.CharField(max_length=255, null=True)
    vol_start = models.DateTimeField()
    vol_end = models.DateTimeField()
    apply_start = models.DateTimeField()
    apply_end = models.DateTimeField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

class Participation(models.Model):
    participation_id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    ATTENDANCE_CHOICES = [
        ('Attend', 'Attend'),
        ('Absent', 'Absent'),
    ]
    attendance = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES, default='Absent')
    apply_date = models.DateTimeField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    event_id = models.ForeignKey(VolunteerEvent, on_delete=models.CASCADE)
    
class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    comment = models.TextField(null=True)
    rating = models.IntegerField(null=True)
    participation_id = models.ForeignKey(Participation, on_delete=models.CASCADE)
    event_id = models.ForeignKey(VolunteerEvent, on_delete=models.CASCADE)