# # from django.db import models
# # from django.contrib.auth.models import User
# # from django.dispatch import receiver
# # from django.db.models.signals import post_save
# # import rsa
# # import base64

# # class Profile(models.Model):
# #     user = models.OneToOneField(User, on_delete=models.CASCADE)
# #     profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.jpg')

# #     def __str__(self):
# #         return f"{self.user.username}'s Profile"

# # @receiver(post_save, sender=User)
# # def create_or_update_user_profile(sender, instance, created, **kwargs):
# #     if created:
# #         Profile.objects.create(user=instance)
# #     else:
# #         instance.profile.save()

# # @receiver(post_save, sender=User)
# # def create_user_keys(sender, instance, created, **kwargs):
# #     if created:
# #         public_key, private_key = UserKeys.generate_keys()
# #         UserKeys.objects.create(user=instance, public_key=public_key, private_key=private_key)
# #     else:
# #         UserKeys.objects.get_or_create(user=instance)  # Ensure key exists

# # class Message(models.Model):
# #     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
# #     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
# #     encrypted_text = models.TextField()
# #     timestamp = models.DateTimeField(auto_now_add=True, db_index=True)  # Index for performance
# #     read_status = models.BooleanField(default=False)  # New field to track read messages
# #     deleted = models.BooleanField(default=False)  # Soft delete flag

# #     def save(self, *args, **kwargs):
# #         receiver_keys = UserKeys.objects.get(user=self.receiver)
# #         public_key = rsa.PublicKey.load_pkcs1(receiver_keys.public_key.encode())
# #         self.encrypted_text = base64.b64encode(rsa.encrypt(self.encrypted_text.encode(), public_key)).decode()
# #         super().save(*args, **kwargs)

# #     def get_decrypted_text(self):
# #         try:
# #             sender_keys = UserKeys.objects.get(user=self.sender)
# #             return UserKeys.decrypt_message(self.encrypted_text, sender_keys.private_key)
# #         except Exception as e:
# #             print(f"Decryption Error: {e}")
# #             return "[Error: Decryption failed]"

# #     class Meta:
# #         ordering = ['-timestamp']

# # class UserKeys(models.Model):
# #     user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
# #     public_key = models.TextField()
# #     private_key = models.TextField()  # New: Store encrypted private key

# #     @staticmethod
# #     def generate_keys():
# #         public_key, private_key = rsa.newkeys(2048)
# #         return public_key.save_pkcs1().decode(), private_key.save_pkcs1().decode()

# #     @staticmethod
# #     def encrypt_message(message, public_key_str):
# #         public_key = rsa.PublicKey.load_pkcs1(public_key_str.encode())
# #         encrypted_data = rsa.encrypt(message.encode(), public_key)
# #         return base64.b64encode(encrypted_data).decode()

# #     @staticmethod
# #     def decrypt_message(encrypted_message, private_key_str):
# #         private_key = rsa.PrivateKey.load_pkcs1(private_key_str.encode())
# #         decrypted_data = rsa.decrypt(base64.b64decode(encrypted_message), private_key)
# #         return decrypted_data.decode()



# # ORIGINAL

# from django.db import models
# from django.contrib.auth.models import User
# from django.dispatch import receiver  # <-- Add this line
# from django.db.models.signals import post_save
# import rsa

# class Profile(models.Model):
#     # One-to-one relationship with Django’s built-in User model
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # Field for profile picture. (Requires Pillow installed: pip install Pillow)
#     profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.jpg')

#     def __str__(self):
#         return f"{self.user.username}'s Profile"

# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#     else:
#         instance.profile.save()

# # @receiver(post_save, sender=User)
# # def create_user_keys(sender, instance, created, **kwargs):
# #     """Ensure that each user has a key pair."""
# #     if created:
# #         public_key, private_key = UserKeys.generate_keys()
# #         UserKeys.objects.create(user=instance, public_key=public_key, private_key=private_key)
# #     else:
# #         UserKeys.objects.get_or_create(user=instance)  # Ensure key exists


# import base64

# class Message(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
#     encrypted_text = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         """Encrypt message with receiver's public key before saving."""
#         receiver_keys = UserKeys.objects.get(user=self.receiver)
#         public_key = rsa.PublicKey.load_pkcs1(receiver_keys.public_key.encode())
#         self.encrypted_text = base64.b64encode(rsa.encrypt(self.encrypted_text.encode(), public_key)).decode()
#         super().save(*args, **kwargs)



#     def get_decrypted_text(self):
#         try:
#             sender_keys = UserKeys.objects.get(user=self.sender)
#             return UserKeys.decrypt_message(self.encrypted_text, sender_keys.private_key)
#         except Exception as e:
#             print(f"Decryption Error: {e}")
#             return "[Error: Decryption failed]"



#     class Meta:
#         ordering = ['-timestamp']



# import base64  # Import base64 for encoding

# # class UserKeys(models.Model):
# #     user = models.OneToOneField(User, on_delete=models.CASCADE)
# #     public_key = models.TextField()
# #     private_key = models.TextField()  # ✅ Ensure this field exists


# #     @staticmethod
# #     def generate_keys():
# #         """Generate RSA key pair but store only the public key in DB."""
# #         public_key, private_key = rsa.newkeys(2048)
# #         return public_key.save_pkcs1().decode(), private_key.save_pkcs1().decode()


# #     @staticmethod
# #     def encrypt_message(message, public_key_str):
# #         """Encrypt message with receiver's public key and encode it in Base64"""
# #         public_key = rsa.PublicKey.load_pkcs1(public_key_str.encode())
# #         encrypted_data = rsa.encrypt(message.encode(), public_key)
# #         return base64.b64encode(encrypted_data).decode()  # Store as Base64

# #     @staticmethod
# #     def decrypt_message(encrypted_message, private_key_str):
# #         """Decode Base64 and decrypt message using private key"""
# #         private_key = rsa.PrivateKey.load_pkcs1(private_key_str.encode())
# #         decrypted_data = rsa.decrypt(base64.b64decode(encrypted_message), private_key)
# #         return decrypted_data.decode()  # Convert back to string
