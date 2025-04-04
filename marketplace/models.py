from django.db import models
from django.contrib.auth.models import User
from profile_app.models import UserProfile  
import uuid
from encrypted_model_fields.fields import EncryptedTextField

class Wallet(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="wallet")
    # Store the balance securely as an encrypted text field.
    encrypted_balance = EncryptedTextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.encrypted_balance is None:
            # Initialize with a balance of 1000
            self.encrypted_balance = "1000"
        super().save(*args, **kwargs)

    def get_balance(self):
        try:
            return float(self.encrypted_balance)
        except (TypeError, ValueError):
            return 0.0

    def update_balance(self, amount):
        """
        Update the wallet balance by a given amount.
        Positive values increase balance, negative values decrease it.
        """
        current_balance = self.get_balance()
        new_balance = current_balance + amount
        self.encrypted_balance = str(new_balance)
        self.save()

    def __str__(self):
        return f"{self.user_profile.user.username}'s Wallet Balance: {self.get_balance()}"

class Artifact(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    bidding_price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="marketplace_listings")
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="artifact_images/", blank=True, null=True)
    sold = models.BooleanField(default=False)  # NEW FIELD

    def __str__(self):
        return f"{self.title} - {'SOLD' if self.sold else 'AVAILABLE'}"


class PaymentTransaction(models.Model):
    artifact = models.ForeignKey(Artifact, on_delete=models.CASCADE, related_name="transactions")
    buyer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="marketplace_purchases")
    seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="marketplace_sales")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, 
        choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")],
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_ref = models.CharField(max_length=100, unique=True, default=uuid.uuid4)

    def __str__(self):
        return f"{self.artifact.title} - {self.status}"
