# TermTalk

TermTalk is a small, terminal-based, peer-to-peer chat prototype focused on short-lived, direct messaging sessions. The reference implementation demonstrates the messaging flow, secure cryptographic primitives, and an in-memory room system for tests and demos.

This project is a demonstration / learning implementation. See the Security Audit for deployment recommendations.

## Features
- 🔐 **Strong Cryptography**: ChaCha20-Poly1305 AEAD encryption with X25519 key exchange
- 🛡️ **Security Hardening**: Connection limits, rate limiting, input validation
- 🧅 **Tor Support**: Optional anonymous routing through Tor network
- ⏱️ **Ephemeral Rooms**: TTL-based rooms with automatic cleanup
- 💻 **Simple CLI**: Host and join sessions from the terminal

## Quickstart

### 1. Install Dependencies
```sh
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### 2. Host a Room
```sh
python3 -m src.main
# Choose option 1: Host a room
# Share the Room ID with peers
```

### 3. Join a Room
```sh
python3 -m src.main
# Choose option 2: Join a room
# Enter the Room ID from the host
```

## Tor Support 🧅

Route connections through Tor for enhanced anonymity:

### Prerequisites
Install and start Tor:
```sh
# Debian/Ubuntu
sudo apt install tor
sudo systemctl start tor

# macOS
brew install tor
brew services start tor
```

### Usage
```sh
# Enable Tor routing
python3 -m src.main --tor

# Use custom Tor port
python3 -m src.main --tor --tor-port 9150
```

**Benefits:**
- Anonymous connection routing
- IP address protection
- Network-level privacy
- Access to .onion services (if supported)

**Note:** Both host and client should use Tor for full anonymity. Tor adds latency (~1-2 seconds per connection).

## Running tests
The project includes a small unit test suite. Run:

```sh
python -m unittest discover -v
```

## Security

**Cryptography:** Uses industry-standard ChaCha20-Poly1305 AEAD with X25519 ECDH key exchange.

**Protections:**
- ✅ Connection limits and rate limiting
- ✅ Input validation and size limits
- ✅ Socket timeouts (prevents DoS)
- ✅ Forward secrecy (ephemeral keys)
- ✅ Replay protection (random nonces)
- ✅ Message authentication (Poly1305)

**Deployment Status:** 🟢 Suitable for trusted networks

See `SECURITY_AUDIT.md` and `SECURITY_REFERENCE.md` for details.

## Limitations
- **No MITM protection** without out-of-band key verification
- **Metadata not protected** (use Tor for network-level privacy)
- **Room discovery** is process-local (file-based registry)
- **Room IDs** have 64-bit entropy (hard to guess, but not impossible)
- **Not audited** for high-security use cases

## Contributing
Contributions are welcome. Please open issues for design discussions or feature requests.

