from django.db import models
from django.contrib.auth.models import User

# Create your models here.


    
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


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.message[:20]}"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')  # prevent duplicates

    def __str__(self):
        status = "Accepted" if self.accepted else "Pending"
        return f"{self.from_user.username} → {self.to_user.username} ({status})"
