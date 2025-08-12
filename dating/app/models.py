from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Home(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

class userDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    dob = models.DateField()
    profile = models.ImageField(upload_to='profile/')
    city = models.CharField(max_length=255)
    occupation = models.CharField(max_length=255)
    education = models.CharField(max_length=255)
    hobbies = models.CharField(max_length=255)
    GENDER_CHOOICE = [
        ('male', "Male"),
        ('female', "Female"),
        ('other', "other"),
    ]
    gender = models.CharField(max_length=50, choices=GENDER_CHOOICE)
    
    def __str__(self):
        return f"{self.user.username} - userDetails"
    

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=50)
    message = models.TextField()

    def __str__(self):
        return f'"{self.name}" send message with this "{self.subject}" subject'

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()

    def __str__(self):
        return self.question

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender.username} to {self.receiver.username}: {self.content}'
