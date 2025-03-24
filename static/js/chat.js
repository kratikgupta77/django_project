let selectedUser = document.getElementById("user-select").value;  // Get the selected username
let socket = new WebSocket(`ws://${window.location.host}/ws/chat/${selectedUser}/`);

// const socket = new WebSocket(`wss://192.168.2.246:8001/ws/chat/${roomName}/`);

socket.onopen = function () {
    console.log("WebSocket connection established.");
};

socket.onerror = function (error) {
    console.error("WebSocket error:", error);
};

socket.onclose = function (event) {
    console.warn("WebSocket closed:", event);
};

socket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    const chatBox = document.getElementById("chatBox");

    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", data.sender === userName ? "sent" : "received");
    messageDiv.innerHTML = `<strong>${data.sender}:</strong> ${data.message}`;

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
};

function sendMessage() {
    const messageInput = document.getElementById("messageInput");
    const userSelect = document.getElementById("userSelect");

    if (userSelect.value === "") {
        alert("Please select a user first.");
        return;
    }

    if (messageInput.value.trim() === "") return;

    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            "message": messageInput.value,
            "sender": userName,
            "receiver": userSelect.value
        }));
        messageInput.value = "";
    } else {
        console.error("WebSocket is not open. Current state:", socket.readyState);
    }
}
