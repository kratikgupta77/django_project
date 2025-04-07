// keymanage.js

const DB_NAME = "pkiKeys";
const STORE_NAME = "keyStore";

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, 1);
        request.onupgradeneeded = function(event) {
            event.target.result.createObjectStore(STORE_NAME);
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function storePrivateKey(privateKey) {
    // Export private key in PKCS8 format
    const exportedKey = await crypto.subtle.exportKey("pkcs8", privateKey);
    const base64 = btoa(String.fromCharCode(...new Uint8Array(exportedKey)));
    const pem = `-----BEGIN PRIVATE KEY-----\n${base64.match(/.{1,64}/g).join("\n")}\n-----END PRIVATE KEY-----`;
    
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    await store.put(pem, "privateKey");
}

async function loadPrivateKey() {
    const db = await openDB();
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const pem = await store.get("privateKey");

    if (!pem || typeof pem !== "string") {
        throw new Error("Private key not found or not stored as a string in IndexedDB");
    }
    // Remove header/footer and whitespace
    const base64 = pem
        .replace(/-----BEGIN PRIVATE KEY-----/, "")
        .replace(/-----END PRIVATE KEY-----/, "")
        .replace(/\s+/g, "");
    const binaryString = atob(base64);
    const len = binaryString.length;
    const buffer = new ArrayBuffer(len);
    const view = new Uint8Array(buffer);
    for (let i = 0; i < len; i++) {
        view[i] = binaryString.charCodeAt(i);
    }
    return await crypto.subtle.importKey(
        "pkcs8",
        buffer,
        { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
        false,
        ["sign"]
    );
}

async function generateAndUploadKeyPair() {
    const keyPair = await crypto.subtle.generateKey(
        {
            name: "RSASSA-PKCS1-v1_5",
            modulusLength: 2048,
            publicExponent: new Uint8Array([1, 0, 1]),
            hash: "SHA-256"
        },
        true,
        ["sign", "verify"]
    );

    // Store private key as a PEM string in IndexedDB
    await storePrivateKey(keyPair.privateKey);

    // Export public key and convert to PEM
    const publicKeyBuffer = await crypto.subtle.exportKey("spki", keyPair.publicKey);
    const publicKeyString = String.fromCharCode(...new Uint8Array(publicKeyBuffer));
    const publicKeyBase64 = btoa(publicKeyString);
    const pemPublicKey = `-----BEGIN PUBLIC KEY-----\n${publicKeyBase64.match(/.{1,64}/g).join("\n")}\n-----END PUBLIC KEY-----`;

    // Upload public key to the server
    await fetch("/marketplace/upload-public-key/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ public_key: pemPublicKey })
    });
}
