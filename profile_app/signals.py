from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from django.contrib.auth.models import User

from marketplace.models import Wallet  # Import Wallet from marketplace app

@receiver(post_save, sender=UserProfile)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user_profile=instance)

@receiver(post_save, sender=UserProfile)
def save_wallet(sender, instance, **kwargs):
    if hasattr(instance, 'wallet'):
        instance.wallet.save()



from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Generate RSA key pair
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        # Serialize public key to PEM format
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        # Create the UserProfile with public_key
        UserProfile.objects.create(user=instance, public_key=public_pem)
