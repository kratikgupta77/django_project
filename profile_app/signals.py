from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from marketplace.models import Wallet  # Import Wallet from marketplace app

@receiver(post_save, sender=UserProfile)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user_profile=instance)

@receiver(post_save, sender=UserProfile)
def save_wallet(sender, instance, **kwargs):
    if hasattr(instance, 'wallet'):
        instance.wallet.save()
