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

    
class Like(models.Model):
    from_user = models.ForeignKey(User, related_name='likes_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='likes_received', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Meta:
    unique_together = ('from_user', 'to_user')

class Match(models.Model):
    user1 = models.ForeignKey(User, related_name='matches1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='matches2', on_delete=models.CASCADE)
    matched_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.recipient}: {self.content[:30]}"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.message[:20]}"