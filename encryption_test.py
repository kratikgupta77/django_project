import os
import sqlite3
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def generate_rsa_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_pem, public_pem

def store_public_key_in_db(user_id, public_key_pem, db_file="keys.db"):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_keys (
            user_id TEXT PRIMARY KEY,
            public_key TEXT NOT NULL
        )
    """)
    cursor.execute("""
        INSERT INTO user_keys (user_id, public_key)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET public_key = excluded.public_key
    """, (user_id, public_key_pem.decode()))
    conn.commit()
    conn.close()

def fetch_public_key_from_db(user_id, db_file="keys.db"):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT public_key FROM user_keys WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0].encode() if result else None

def encrypt_and_store_private_key(private_key_pem, password, filename="private_key.pem.enc"):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    key = kdf.derive(password.encode())
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    encrypted_key = encryptor.update(private_key_pem) + encryptor.finalize()
    with open(filename, "wb") as f:
        f.write(salt + iv + encrypted_key)

def load_private_key(filename="private_key.pem.enc", password="strong-password"):
    with open(filename, "rb") as f:
        data = f.read()
    salt, iv, encrypted_key = data[:16], data[16:32], data[32:]
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    key = kdf.derive(password.encode())
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    decrypted_key = decryptor.update(encrypted_key) + decryptor.finalize()
    return serialization.load_pem_private_key(decrypted_key, password=None)

def encrypt_message(message, recipient_public_key_pem):
    recipient_public_key = serialization.load_pem_public_key(recipient_public_key_pem)
    return recipient_public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_message(encrypted_message, private_key):
    return private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()

# --- TESTING ---
user_id = "test_user"
password = "strong-password"

# Generate and store keys
private_pem, public_pem = generate_rsa_key_pair()
store_public_key_in_db(user_id, public_pem)
encrypt_and_store_private_key(private_pem, password, "test_private_key.pem.enc")

# Retrieve public key
retrieved_public_pem = fetch_public_key_from_db(user_id)
assert retrieved_public_pem == public_pem, "Public key mismatch!"

# Encrypt message
message = "Hello, secure world!"
encrypted_message = encrypt_message(message, retrieved_public_pem)
print(f"Encrypted: {encrypted_message.hex()}")

# Decrypt message
private_key = load_private_key("test_private_key.pem.enc", password)
decrypted_message = decrypt_message(encrypted_message, private_key)
assert message == decrypted_message, "Decryption failed!"
print(f"Decrypted: {decrypted_message}")

print("✅ End-to-End Encryption Test Passed!")


from django.db import models
from django.contrib.auth.models import User
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", default="profile_pics/default.jpg", blank=True, null=True)
    public_key = models.TextField(blank=True, null=True)  # Store Public Key

    def __str__(self):
        return self.user.username

    def generate_keys(self):
        """Generates a public-private key pair and stores them securely."""
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        # Store the public key in the database
        self.public_key = public_pem
        self.save()

        # Encrypt and store the private key locally
        self.store_private_key(private_pem)

    def store_private_key(self, private_pem, password="strong-password"):
        """Encrypts and stores the private key on the user's system."""
        user_private_key_path = f"{self.user.username}_private_key.pem.enc"
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        key = kdf.derive(password.encode())
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
        encryptor = cipher.encryptor()
        encrypted_key = encryptor.update(private_pem) + encryptor.finalize()

        with open(user_private_key_path, "wb") as f:
            f.write(salt + iv + encrypted_key)

    def get_private_key(self, password="strong-password"):
        """Retrieves and decrypts the private key from local storage."""
        user_private_key_path = f"{self.user.username}_private_key.pem.enc"
        if not os.path.exists(user_private_key_path):
            raise ValueError("Private key file not found.")

        with open(user_private_key_path, "rb") as f:
            data = f.read()

        salt, iv, encrypted_key = data[:16], data[16:32], data[32:]
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        key = kdf.derive(password.encode())
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
        decryptor = cipher.decryptor()
        decrypted_key = decryptor.update(encrypted_key) + decryptor.finalize()

        return serialization.load_pem_private_key(decrypted_key, password=None)

    def get_public_key(self):
        """Loads the user's public key safely."""
        if not self.public_key:
            raise ValueError("Public key is not available.")
        return serialization.load_pem_public_key(self.public_key.encode())


# Automatically generate keys when a new UserProfile is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=UserProfile)
def create_user_keys(sender, instance, created, **kwargs):
    if created:
        instance.generate_keys()

