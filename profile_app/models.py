from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedTextField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", default="profile_pics/default.jpg", blank=True, null=True)
    public_key = models.TextField(blank=True, null=True)
    # Note: Do NOT store private keys in the database.
    def __str__(self):
        return self.user.username

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = EncryptedTextField()  # Encrypt the message text
    timestamp = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ['-timestamp']
    def __str__(self):
        return f"{self.sender.username}: {self.text}"  # Decrypt text when printing
