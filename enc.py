import os
import json
import base64
from flask import Flask, render_template_string, request, redirect, url_for
from flask_socketio import SocketIO, join_room, emit
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# --- Cryptographic Functions ---

def generate_rsa_keys():
    """Generate an RSA private/public key pair."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def encrypt_message(message: str, receiver_public_key) -> str:
    """
    Encrypts a message using a randomly generated symmetric key (AES-GCM)
    and then encrypts that symmetric key with the receiver's RSA public key.
    Returns a JSON string with all encrypted components, base64-encoded.
    """
    symmetric_key = os.urandom(32)  # 256-bit key for AES
    nonce = os.urandom(12)          # 96-bit nonce for AES-GCM

    # Encrypt the message with AES-GCM
    encryptor = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce)).encryptor()
    ciphertext = encryptor.update(message.encode('utf-8')) + encryptor.finalize()
    tag = encryptor.tag

    # Encrypt the symmetric key using the receiver's RSA public key
    encrypted_sym_key = receiver_public_key.encrypt(
        symmetric_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Bundle all components in a dictionary (base64-encoded for safe transmission)
    payload = {
        'encrypted_sym_key': base64.b64encode(encrypted_sym_key).decode('utf-8'),
        'nonce': base64.b64encode(nonce).decode('utf-8'),
        'tag': base64.b64encode(tag).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
    }
    return json.dumps(payload)

def decrypt_message(encrypted_data: str, receiver_private_key) -> str:
    """
    Decrypts the JSON payload produced by encrypt_message.
    Returns the decrypted plaintext message.
    """
    try:
        payload = json.loads(encrypted_data)
        encrypted_sym_key = base64.b64decode(payload['encrypted_sym_key'])
        nonce = base64.b64decode(payload['nonce'])
        tag = base64.b64decode(payload['tag'])
        ciphertext = base64.b64decode(payload['ciphertext'])

        # Decrypt the symmetric key using RSA private key
        symmetric_key = receiver_private_key.decrypt(
            encrypted_sym_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt the ciphertext using AES-GCM
        decryptor = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce, tag)).decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode('utf-8')
    except Exception as e:
        return f"Decryption Error: {e}"

# --- User Class ---

class User:
    def __init__(self, name):
        self.name = name
        self.private_key, self.public_key = generate_rsa_keys()

# Instantiate two users: User A and User B
user_a = User("User A")
user_b = User("User B")

# --- Flask and Socket.IO Setup ---

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# --- HTML Template ---
# Two pages are served:
# 1. A login page where the user chooses their identity (A or B).
# 2. The chat page which uses Socket.IO for real-time updates.
template_login = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Login - Encrypted Chat</title>
</head>
<body>
  <h1>Login</h1>
  <form action="/chat" method="get">
    <label for="user">Choose User:</label>
    <select name="user" id="user">
      <option value="A">User A</option>
      <option value="B">User B</option>
    </select>
    <input type="submit" value="Enter Chat">
  </form>
</body>
</html>
"""

template_chat = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Encrypted Chat - User {{ user }}</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/3.1.3/socket.io.min.js"></script>
</head>
<body>
  <h1>Encrypted Chat - Logged in as User {{ user }}</h1>
  <div id="chat" style="border:1px solid #333; height:300px; width:500px; overflow-y:scroll; padding:10px;"></div>
  <br>
  <input type="text" id="message" placeholder="Type your message here..." style="width:400px;">
  <button onclick="sendMessage()">Send</button>

  <script type="text/javascript">
    var socket = io();
    // Join a room based on the user identity
    var user = "{{ user }}";
    socket.emit("join", {"user": user});

    // Listen for incoming messages
    socket.on("new_message", function(data) {
      var chat = document.getElementById("chat");
      var msg = document.createElement("p");
      msg.innerHTML = "<strong>" + data.sender + " to " + data.receiver + ":</strong> " +
                      "Original: " + data.original_message + "<br>" +
                      "Decrypted: " + data.decrypted_message;
      chat.appendChild(msg);
      chat.scrollTop = chat.scrollHeight;
    });

    function sendMessage() {
      var msgInput = document.getElementById("message");
      var msg = msgInput.value;
      if(msg.trim() === "") return;
      socket.emit("send_message", {"sender": user, "message": msg});
      msgInput.value = "";
    }
  </script>
</body>
</html>
"""

# --- Routes ---

@app.route("/")
def index():
    return render_template_string(template_login)

@app.route("/chat")
def chat():
    user = request.args.get("user", "A")
    # Render the chat interface passing the user type (A or B)
    return render_template_string(template_chat, user=user)

# --- Socket.IO Event Handlers ---

@socketio.on('join')
def on_join(data):
    user = data.get("user", "A")
    join_room(user)  # Each user joins a room named after them
    print(f"{user} joined their room.")

@socketio.on("send_message")
def handle_message(data):
    sender = data.get("sender")
    message = data.get("message")
    if sender not in ["A", "B"] or not message:
        return

    # Determine receiver based on sender
    if sender == "A":
        # Encrypt with User B's public key and decrypt with User B's private key
        encrypted = encrypt_message(message, user_b.public_key)
        decrypted = decrypt_message(encrypted, user_b.private_key)
        receiver = "B"
    else:
        # sender == "B"
        encrypted = encrypt_message(message, user_a.public_key)
        decrypted = decrypt_message(encrypted, user_a.private_key)
        receiver = "A"

    # Prepare the message payload
    msg_payload = {
        "sender": "User " + sender,
        "receiver": "User " + receiver,
        "original_message": message,
        "decrypted_message": decrypted
    }
    # Emit to both sender and receiver rooms
    socketio.emit("new_message", msg_payload, room=receiver)
    socketio.emit("new_message", msg_payload, room=sender)

if __name__ == "__main__":
    socketio.run(app, debug=True)
