from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", default="profile_pics/default.jpg", blank=True, null=True)
    # public_key = models.TextField(blank=True, null=True)  # Store Public Key
    # private_key = models.TextField(blank=True, null=True)  # Store Private Key (Encrypted)

    def __str__(self):
        return self.user.username

    # def generate_keys(self):
    #     """Generates a public-private key pair."""
    #     private_key = rsa.generate_private_key(
    #         public_exponent=65537,
    #         key_size=2048
    #     )
    #     public_key = private_key.public_key()

    #     # Serialize private key
    #     private_pem = private_key.private_bytes(
    #         encoding=serialization.Encoding.PEM,
    #         format=serialization.PrivateFormat.PKCS8,
    #         encryption_algorithm=serialization.NoEncryption()
    #     ).decode()

    #     # Serialize public key
    #     public_pem = public_key.public_bytes(
    #         encoding=serialization.Encoding.PEM,
    #         format=serialization.PublicFormat.SubjectPublicKeyInfo
    #     ).decode()

    #     self.private_key = private_pem
    #     self.public_key = public_pem
    #     self.save()

    # def get_private_key(self):
    #     if not self.private_key:
    #         raise ValueError("Private key is not available.")
    #     return serialization.load_pem_private_key(self.private_key.encode(), password=None)

    # def get_public_key(self):
    #     """Loads the user's public key safely."""
    #     if not self.public_key:
    #         raise ValueError("Public key is not available.")
    #     return serialization.load_pem_public_key(self.public_key.encode())


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    text = models.TextField()  # Ensure 'text' field exists
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']




# from django.db import models
# from django.contrib.auth.models import User

# class Message(models.Model):
#     sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
#     receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
#     encrypted = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.sender} to {self.receiver}: {self.content}"



# from django.db import models
# from django.contrib.auth.models import User
# from cryptography.fernet import Fernet
# import base64

# # Generate a key (store this securely in settings)
# KEY = Fernet.generate_key()
# cipher = Fernet(KEY)

# from django.db import models
# from django.contrib.auth.models import User

# class Message(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
#     content = models.TextField()  # Plaintext messages
#     timestamp = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["-timestamp"]


# # class Message(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
#     encrypted_text = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         self.encrypted_text = cipher.encrypt(self.encrypted_text.encode()).decode()
#         super().save(*args, **kwargs)

#     def get_decrypted_text(self):
#         return cipher.decrypt(self.encrypted_text.encode()).decode()
    
#     # def encrypt_message(self, plain_text, receiver_public_key):
#     #     """Encrypts message using the receiver's public key."""
#     #     encrypted = receiver_public_key.encrypt(
#     #         plain_text.encode(),
#     #         padding.OAEP(
#     #             mgf=padding.MGF1(algorithm=hashes.SHA256()), #USES SHA256 algo
#     #             algorithm=hashes.SHA256(),
#     #             label=None
#     #         )
#     #     )
#     #     return encrypted.hex()  # Store as hex string

#     # def decrypt_message(self, receiver_private_key):
#     #     """Decrypts the stored message."""
#     #     decrypted = receiver_private_key.decrypt(
#     #         bytes.fromhex(self.encrypted_content),
#     #         padding.OAEP(
#     #             mgf=padding.MGF1(algorithm=hashes.SHA256()),
#     #             algorithm=hashes.SHA256(),
#     #             label=None
#     #         )
#     #     )
#     #     return decrypted.decode()

#     class Meta:
#         ordering = ['-timestamp']



# class Message(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
#     encrypted_content = models.TextField(default="")  # Store encrypted messages
#     timestamp = models.DateTimeField(auto_now_add=True)
#     content = models.TextField()  # 🔹 Make sure this exists!


#     def encrypt_message(self, plain_text, receiver_public_key):
#         """Encrypts message using the receiver's public key."""
#         encrypted = receiver_public_key.encrypt(
#             plain_text.encode(),
#             padding.OAEP(
#                 mgf=padding.MGF1(algorithm=hashes.SHA256()), #this thing
#                 algorithm=hashes.SHA256(),
#                 label=None
#             )
#         )
#         return encrypted.hex()  # Store as hex string

#     def decrypt_message(self, receiver_private_key):
#         """Decrypts the stored message."""
#         decrypted = receiver_private_key.decrypt(
#             bytes.fromhex(self.encrypted_content),
#             padding.OAEP(
#                 mgf=padding.MGF1(algorithm=hashes.SHA256()),
#                 algorithm=hashes.SHA256(),
#                 label=None
#             )
#         )
#         return decrypted.decode()

#     def save(self, *args, **kwargs):
#         """Encrypts message content before saving."""
#         receiver_profile = UserProfile.objects.get(user=self.receiver)
#         receiver_public_key = receiver_profile.get_public_key()
#         self.encrypted_content = self.encrypt_message(self.content, receiver_public_key)  # Encrypt content, not encrypted_content
#         self.content = ""  # Clear plain text content before saving
#         super().save(*args, **kwargs)



# class MediaMessage(models.Model):
#     sender = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='sent_media_messages'
#     )  # 🔹 Give a unique related_name

#     receiver = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name='received_media_messages'
#     )  # 🔹 Give a unique related_name

#     media_file = models.FileField(upload_to='media_messages/')
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"MediaMessage from {self.sender} to {self.receiver}"
