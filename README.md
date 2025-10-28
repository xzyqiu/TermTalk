# 🗨️ Secure Encrypted CLI Messaging

**Terminal Chat** is a lightweight, end-to-end encrypted messaging app that runs entirely in your terminal.  
It lets two users communicate securely over a direct socket connection — no servers, no cloud, just your terminal and an IP address.

## 🔒 Features
- **End-to-End Encryption** — Messages are protected with modern cryptography.  
- **Peer-to-Peer Communication** — Direct socket connections between host and guest.  
- **Cross-Platform** — Works anywhere Python does (Linux, macOS, Windows).  
- **Simple Setup** — Start a chat room or join one using an IP and port.  
- **Fully Terminal-Based** — Minimalist interface for secure command-line use.

## 🚀 Quick Start
1. Install dependencies:
   pip install -r requirements.txt

2. Start the host:
   python -m src.main host

3. Join as a guest from another terminal or device:
   python -m src.main join

4. Chat securely in your terminal window!

## ⚙️ Security
All messages are encrypted end-to-end using session keys established during a handshake phase.  
No plaintext is ever transmitted over the network.
