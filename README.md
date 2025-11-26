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
# For LAN: enter your local IP (e.g., 192.168.1.100)
# For Internet: enter 0.0.0.0 + forward port on router, share public IP
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
# If Room ID not in local registry (LAN/Internet):
#   - Enter host's IP address (e.g., 192.168.1.100 or public IP)
#   - Enter port (default: 12345)
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

## Network Connectivity

TermTalk supports **localhost, LAN, and internet** connections:

### Localhost (Default - Most Secure)
```sh
# Host binds to 127.0.0.1 - only accessible from same machine
Host IP: 127.0.0.1
Port: 12345
```
**Use case:** Testing, same-machine communication

### LAN (Local Network)
```sh
# Host binds to local IP (e.g., 192.168.1.100)
Host IP: 192.168.1.100
Port: 12345
```
**Use case:** Private network, trusted devices
**Security:** Protected by network firewall

### Internet (Requires Port Forwarding)
```sh
# Host binds to 0.0.0.0 (all interfaces)
Host IP: 0.0.0.0
Port: 12345
```
**Steps for Host:**
1. Forward port 12345 on your router to host machine's local IP
2. Find your public IP: `curl ifconfig.me` 
3. Share with peer: **Room ID + your public IP + port**

**Steps for Peer:**
1. Run `python3 -m src.main` and choose "Join a room"
2. Enter the Room ID (16 chars)
3. When prompted "Room not found in local registry":
   - Enter host's **public IP** (e.g., 203.0.113.45)
   - Enter **port** (e.g., 12345)
4. Connection established with end-to-end encryption!

**Example:**
```sh
# Host (public IP: 203.0.113.45)
python3 -m src.main
> Host a room
> IP: 0.0.0.0
> Port: 12345
> Room ID: a3f5d7b9e2c4f6a8

# Peer (anywhere on internet)
python3 -m src.main
> Join a room  
> Room ID: a3f5d7b9e2c4f6a8
> Room not found in local registry
> Host IP: 203.0.113.45
> Port: 12345
✅ Connected!
```

**Security recommendations:**
- ⚠️ Use `--tor` flag to hide your public IP
- ⚠️ Use VPN if you don't want to expose home IP
- ⚠️ Keep room TTL short (default 5 min)
- ⚠️ Be aware: No MITM protection (key fingerprint verification not implemented)

**Registry Note:** The file-based registry (`~/.termtalk_rooms.json`) only works for same-machine discovery. For LAN/internet, the peer will be prompted to enter host IP:port directly.

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
- **`docs/INTERNET_CONNECTIVITY.md`**: Complete guide for internet/LAN connections
- **`docs/PRIVACY.md`**: Privacy protections and anonymity guarantees
- **`docs/threat_model.md`**: Threat analysis and mitigations
- **`docs/TOR_GUIDE.md`**: Tor integration and anonymity guide

## Known Limitations
- ⚠️ **No MITM protection**: Key exchange lacks fingerprint verification (trust-on-first-use)
- ⚠️ **Metadata exposure**: Without Tor, IP addresses and timing visible to network observers
- ⚠️ **Local registry only**: File-based registry (~/.termtalk_rooms.json) for same-machine discovery
  - **Workaround**: Manually share host IP:port for LAN/internet connections
  - Connections work over any network (localhost/LAN/internet)
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

