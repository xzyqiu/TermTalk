# 🗨️ Secure Encrypted CLI Messaging

**Terminal Chat** is a lightweight, end-to-end encrypted messaging app that runs entirely in your terminal.  
It lets two users communicate securely over a direct socket connection — no servers, no cloud, just your terminal and an IP address.

## 🔒 Features
- **End-to-End Encryption** — Messages are protected with modern cryptography.  
- **Peer-to-Peer Communication** — Direct socket connections between host and guest.  
- **Cross-Platform** — Works anywhere Python does (Linux, macOS, Windows).  
- **Simple Setup** — Start a chat room or join one using an IP and port.  
- **Fully Terminal-Based** — Minimalist interface for secure command-line use.  
- **Lightweight and Minimal Dependencies** — Easy to install and run.

## 🚀 Quick Start

1. Clone the repository:
   ```git clone https://github.com/yourusername/terminal-chat.git```
   ```cd terminal-chat```

2. Create and activate a virtual environment:
   ```python -m venv venv```
   ```source venv/bin/activate   # Linux/macOS```
   ```venv\Scripts\activate      # Windows```

3. Install dependencies:
   ```pip install -r requirements.txt```

4. Start the host:
   ```python -m src.main host```

5. Join as a guest from another terminal or device:
   ```python -m src.main join```

6. Chat securely in your terminal window!

## ⚙️ Security
All messages are encrypted end-to-end using session keys established during a handshake phase.  
No plaintext is ever transmitted over the network.  
Your data is safe even if the network is compromised.

## 🧠 How It Works
- **Handshake Phase:** Host and guest exchange public keys to establish a secure session key.  
- **Message Encryption:** Every message is encrypted using the session key before being sent.  
- **Direct Socket Communication:** Messages travel directly between peers; no third-party server involved.


## 📸 Demo
*A screenshot or terminal GIF here would be great to show the chat in action.*

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.  
Make sure your code passes existing tests and follows the project structure.

## 🏷️ Topics
Python, CLI, Chat, Peer-to-Peer, Encryption, Socket, Secure Messaging
