from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)  # First Name
    last_name = models.CharField(max_length=30, blank=True, null=True)  # Last Name
    profile_picture = models.ImageField(upload_to="profile_pics/", default="profile_pics/default.jpg", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.first_name} {self.last_name})"

    def get_full_name(self):
        """Returns the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip() if self.first_name or self.last_name else self.user.username
