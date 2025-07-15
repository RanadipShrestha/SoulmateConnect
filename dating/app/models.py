from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    dob = models.DateField()
    profile = models.ImageField(upload_to='profile/')
    city = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    education = models.CharField(max_length=255)
    hobbies = models.CharField(max_length=255)
    GENDER_CHOICES = [
        ('male', "Male"),
        ('female', "Female"),
        ('other', "other"),
    ]
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES)
    
    def __str__(self):
        return f"{self.user.username} - UserDetails"