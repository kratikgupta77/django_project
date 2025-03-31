from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedTextField

# Existing models...
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", default="profile_pics/default.jpg", blank=True, null=True)
    public_key = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.user.username

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = EncryptedTextField()  # encrypts message text
    timestamp = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.text}"

# --- New Group Messaging Models ---

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='group_memberships')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages')
    text = models.TextField()  # plain text for now (encryption skipped)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        # show first 20 characters
        return f"{self.sender.username}: {self.text[:20]}"
