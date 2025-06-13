from django.db import models
from django.contrib.auth.models import User


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('interview', 'Interview'),
        ('offer', 'Offer'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_date = models.DateField()
    notes = models.TextField(blank=True, null=True)  # New field
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)  # New field

    def __str__(self):
        return f"{self.position} at {self.company}"
