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


from django.db import models
from django.contrib.auth.models import User

class Like(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liker')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user} liked {self.to_user}"

class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches2')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match between {self.user1} and {self.user2}"
