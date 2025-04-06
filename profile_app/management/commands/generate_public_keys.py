from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profile_app.models import UserProfile  

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class Command(BaseCommand):
    help = 'Generate public keys for users who are missing them.'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        count_updated = 0

        for user in users:
            try:
                profile = user.userprofile
                if not profile.public_key:
                    # Generate key pair
                    private_key = rsa.generate_private_key(
                        public_exponent=65537,
                        key_size=2048,
                    )
                    public_key = private_key.public_key()

                    # Convert to PEM format
                    public_pem = public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ).decode()

                    profile.public_key = public_pem
                    profile.save()
                    self.stdout.write(self.style.SUCCESS(f" Added public key for {user.username}"))
                    count_updated += 1
                else:
                    self.stdout.write(f" Public key already exists for {user.username}")
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.WARNING(f" No UserProfile found for {user.username}"))

        self.stdout.write(self.style.SUCCESS(f"\nDone! Public keys generated for {count_updated} user(s)."))
