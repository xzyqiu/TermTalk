# TermTalk

TermTalk is a small, terminal-based, peer-to-peer chat prototype focused on short-lived, direct messaging sessions. The reference implementation demonstrates the messaging flow, secure cryptographic primitives, and an in-memory room system for tests and demos.

This project is a demonstration / learning implementation. See the Security Audit for deployment recommendations.

## Features
- 🔐 **Strong Cryptography**: ChaCha20-Poly1305 AEAD encryption with X25519 ECDH key exchange
- 🛡️ **Security Hardening**: Connection limits (5 per IP, 50 global), rate limiting (10/min per IP), input validation
- 🕵️ **Privacy-First**: No MAC addresses, hostnames, or system metadata exposed - ephemeral IDs only
- 🧅 **Tor Support**: Optional anonymous routing through Tor SOCKS5 proxy
- ⏱️ **Ephemeral Rooms**: TTL-based rooms (default 5 min) with automatic cleanup
- 🔔 **Real-time Notifications**: Visual alerts for joins, leaves, and connection status
- 💻 **Simple CLI**: Host and join sessions from the terminal with colored output
- 🔒 **Forward Secrecy**: Ephemeral X25519 keys per session

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
# Default: binds to 127.0.0.1 (localhost only - secure)
# For LAN access: enter your local IP (e.g., 192.168.1.100)
# Share the Room ID (16 chars) with peers
```

**Example output:**
```
[CLI] Room created! Room ID: d0933719af4a4c89
[CLI] Waiting for peers... (expires in 300s)

✅ Peer 192.168.1.100 joined the room! (1 peer(s) connected)
[48504] [11:45:44] ME: Hello!
```

### 3. Join a Room
```sh
python3 -m src.main
# Choose option 2: Join a room
# Enter the 16-character Room ID from the host
```

**Example output:**
```
✅ Successfully connected to 192.168.1.1:12345
🔒 Secure encrypted channel established

Type your messages and press Enter to send...
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

## Running Tests
The project includes comprehensive test coverage (18 tests):

```sh
# Activate venv first
source venv/bin/activate

# Run all tests
python3 -m unittest discover -s tests -v

# Run specific test suites
python3 -m unittest tests.test_crypto -v       # Crypto tests
python3 -m unittest tests.test_security -v     # Security tests
python3 -m unittest tests.test_handshake -v    # Key exchange tests
```

**Test Coverage:**
- ✅ ChaCha20-Poly1305 encryption/decryption
- ✅ X25519 ECDH key exchange
- ✅ Connection limiting and rate limiting
- ✅ Input validation and size limits
- ✅ Message authentication and tampering detection
- ✅ Replay protection (nonce randomization)

## Security

### Cryptographic Primitives
- **Encryption**: ChaCha20-Poly1305 AEAD (256-bit keys, 96-bit nonces, 128-bit auth tags)
- **Key Exchange**: X25519 ECDH with HKDF-SHA256 key derivation
- **Forward Secrecy**: Ephemeral key pairs generated per session
- **Authentication**: Poly1305 MAC prevents tampering
- **Replay Protection**: Random nonces ensure unique ciphertexts

### Security Controls
| Protection | Implementation | Limit |
|------------|----------------|-------|
| **Connection Limiting** | Per-IP + Global | 5 per IP, 50 total |
| **Rate Limiting** | Time-based tracking | 10 connections/min per IP |
| **Input Validation** | Size + format checks | 512B keys, 64KB messages |
| **Socket Timeouts** | Connection + operation | 30-60 seconds |
| **Room ID Entropy** | UUID-based generation | 64 bits (18 quintillion) |
| **File Permissions** | Registry protection | 0600 (owner-only) |

### Deployment Status
🟢 **Suitable for trusted networks** (development, testing, LANs)  
🟡 **Use with caution** on public networks (consider Tor)  
🔴 **Not recommended** for high-security or production use without additional hardening

### Documentation
- **`SECURITY_AUDIT.md`**: Comprehensive vulnerability assessment and fixes
- **`SECURITY_FIXES.md`**: Detailed changelog of security improvements
- **`SECURITY_REFERENCE.md`**: Quick reference for security features
- **`docs/PRIVACY.md`**: Privacy protections and anonymity guarantees
- **`docs/threat_model.md`**: Threat analysis and mitigations
- **`docs/TOR_GUIDE.md`**: Tor integration and anonymity guide

## Known Limitations
- ⚠️ **No MITM protection**: Key exchange lacks fingerprint verification (trust-on-first-use)
- ⚠️ **Metadata exposure**: Without Tor, IP addresses and timing visible to network observers
- ⚠️ **Local room discovery**: File-based registry (~/.termtalk_rooms.json) for same-machine sessions
- ⚠️ **Room ID enumeration**: 64-bit entropy is strong but theoretically brute-forceable
- ⚠️ **No formal audit**: Educational/demo project, not professionally audited

### Recommendations for Production
1. **Add key fingerprint verification** to detect MITM attacks
2. **Implement distributed registry** (Redis/etcd) for cross-machine discovery
3. **Use Tor by default** for metadata protection
4. **Add room passwords** for additional authentication layer
5. **Professional security audit** before any production deployment

## Project Structure
```
TermTalk/
├── src/
│   ├── cli/            # Command-line interface
│   ├── crypto/         # Encryption (ChaCha20-Poly1305, X25519)
│   ├── room/           # Room management and registry
│   ├── transport/      # Socket handlers and Tor integration
│   └── utils/          # Helper functions
├── tests/              # Unit and security tests
├── docs/               # Documentation (threat model, Tor guide)
├── SECURITY_*.md       # Security audit, fixes, and reference
└── requirements.txt    # Dependencies
```

## Command-Line Options
```sh
python3 -m src.main [OPTIONS]

Options:
  -h, --help              Show help message
  --tor                   Route through Tor (requires Tor daemon)
  --tor-port PORT         Custom Tor SOCKS5 port (default: 9050)
```

## Contributing
Contributions are welcome! Please:
- Open issues for bugs or feature requests
- Submit PRs with tests for new features
- Follow existing code style (black + ruff)
- Update documentation for significant changes

See `tests/` for examples of how to write tests.

## License
See `LICENSE` file for details.

