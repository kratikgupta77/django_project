from django.db import models
from django.contrib.auth.models import User
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", default="profile_pics/default.jpg", blank=True, null=True)
    public_key = models.TextField(blank=True, null=True)  # Store Public Key
    private_key = models.TextField(blank=True, null=True)  # Store Private Key (Encrypted)

    def __str__(self):
        return self.user.username

    def generate_keys(self):
        """Generates a public-private key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()

        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        self.private_key = private_pem
        self.public_key = public_pem
        self.save()

    def get_private_key(self):
        if not self.private_key:
            raise ValueError("Private key is not available.")
        return serialization.load_pem_private_key(self.private_key.encode(), password=None)

    def get_public_key(self):
        """Loads the user's public key safely."""
        if not self.public_key:
            raise ValueError("Public key is not available.")
        return serialization.load_pem_public_key(self.public_key.encode())

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    encrypted_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.encrypted_text = cipher.encrypt(self.encrypted_text.encode()).decode()
        super().save(*args, **kwargs)

    def get_decrypted_text(self):
        return cipher.decrypt(self.encrypted_text.encode()).decode()
    
    def encrypt_message(self, plain_text, receiver_public_key):
        """Encrypts message using the receiver's public key."""
        encrypted = receiver_public_key.encrypt(
            plain_text.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()), #USES SHA256 algo
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted.hex()  # Store as hex string

    def decrypt_message(self, receiver_private_key):
        """Decrypts the stored message."""
        decrypted = receiver_private_key.decrypt(
            bytes.fromhex(self.encrypted_content),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode()

    class Meta:
        ordering = ['-timestamp']