# TermTalk — Technical Specification

**Version**: 2.0 (Post-Security-Hardening)  
**Date**: November 26, 2025

## Purpose
TermTalk is a secure, terminal-based peer-to-peer messaging system for ephemeral, encrypted chat sessions. This specification documents the cryptographic protocol, network architecture, and security controls.

## Command-Line Interface

### Main Command
```bash
python3 -m src.main [OPTIONS]
```

**Options:**
- `--tor`: Route connections through Tor SOCKS5 proxy (requires Tor daemon)
- `--tor-port PORT`: Specify custom Tor port (default: 9050)
- `-h, --help`: Display help message

### Interactive Menu
1. **Host a room**: Create ephemeral room and wait for peers
2. **Join a room**: Connect to existing room via Room ID

### Host Configuration (Interactive Prompts)
- **Bind address**: Default `127.0.0.1` (localhost), or custom IP for LAN access
- **Port**: Default `12345`, or custom port
- **TTL**: Default `300` seconds (5 minutes), configurable

### Room ID Format
- **Length**: 16 hexadecimal characters
- **Entropy**: 64 bits (2^64 ≈ 18 quintillion possibilities)
- **Generation**: First 16 chars of UUID v4 (hyphens removed)
- **Example**: `d0933719af4a4c89`

## Protocol Flow

### 1. Room Creation (Host)
```
Host → Creates Room object with random 16-char ID
Host → Registers room in ~/.termtalk_rooms.json (permissions: 0600)
Host → Binds TCP socket to specified IP:port
Host → Sets socket options (SO_REUSEADDR, timeout=30s)
Host → Starts accept loop in background thread
Host → Displays Room ID to user
```

### 2. Connection Establishment (Client → Host)
```
Client → Looks up Room ID in local registry
Client → Retrieves host IP:port from registry entry
Client → Creates TCP socket with timeout (30s)
Client → [Optional] Routes through Tor SOCKS5 if --tor enabled
Client → Connects to host IP:port
```

### 3. Cryptographic Handshake (Both)
```
Host → Generates ephemeral X25519 key pair
Host → Sends Base64(public_key) + "\n" to client

Client → Receives host's public key
Client → Generates ephemeral X25519 key pair
Client → Sends Base64(public_key) + "\n" to host

Both → Perform ECDH: shared_secret = ECDH(private_key, peer_public_key)
Both → Derive session key: key = HKDF-SHA256(shared_secret, info="TermTalk v1 session key")
Both → Initialize ChaCha20Poly1305(key)

Client → Displays "✅ Successfully connected"
Host → Displays "✅ Peer X.X.X.X joined the room"
```

### 4. Message Exchange
```
Sender → Generates random 12-byte nonce
Sender → Encrypts: ciphertext = ChaCha20Poly1305.encrypt(nonce, plaintext)
Sender → Sends Base64(nonce || ciphertext || auth_tag)

Receiver → Receives and decodes Base64
Receiver → Splits: nonce (12B) | ciphertext | tag (16B)
Receiver → Decrypts and authenticates: plaintext = ChaCha20Poly1305.decrypt(nonce, ciphertext)
Receiver → Verifies auth tag (automatic in AEAD)
Receiver → Displays decrypted message
```

### 5. Disconnection
```
Peer → Closes socket (graceful or timeout)
Host → Detects closed connection
Host → Removes from connections dict
Host → Decrements connection counters
Host → Displays "❌ Peer X.X.X.X left the room"
Host → Clears session key from memory
```

### 6. Room Expiration
```
Background thread → Checks TTL every second
If expired → Sets room.active = False
           → Stops host socket
           → Removes from registry
           → Displays "Room expired"
```

## Cryptographic Specification

### Algorithms
| Component | Algorithm | Key Size | Details |
|-----------|-----------|----------|---------|
| **Encryption** | ChaCha20 | 256 bits | Stream cipher (RFC 8439) |
| **Authentication** | Poly1305 | 128-bit tag | MAC for integrity |
| **AEAD** | ChaCha20-Poly1305 | Combined | Encrypt-then-MAC |
| **Key Exchange** | X25519 | 256 bits | Elliptic curve DH (Curve25519) |
| **KDF** | HKDF-SHA256 | 256-bit output | Key derivation function |
| **Nonce** | Random | 96 bits | `os.urandom(12)` |

### Key Derivation
```python
# ECDH to get shared secret
shared_secret = private_key.exchange(peer_public_key)  # 32 bytes

# HKDF to derive session key
session_key = HKDF(
    algorithm=SHA256,
    length=32,
    salt=None,
    info=b"TermTalk v1 session key"
).derive(shared_secret)
```

### Message Format
```
Ciphertext = Base64(nonce || encrypted_data || auth_tag)

Where:
- nonce: 12 bytes (random per message)
- encrypted_data: variable length (plaintext encrypted with ChaCha20)
- auth_tag: 16 bytes (Poly1305 MAC)
```

## Security Controls

### Network Layer
| Control | Value | Purpose |
|---------|-------|---------|
| Max connections (global) | 50 | DoS prevention |
| Max connections per IP | 5 | Single-source DoS prevention |
| Rate limit | 10/min per IP | Connection flood prevention |
| Accept timeout | 30 seconds | Prevent blocked accept() |
| Client timeout | 60 seconds | Detect dead connections |
| Message size limit | 64 KB | Buffer overflow prevention |
| Public key size limit | 512 bytes | Input validation |

### Application Layer
- **Default binding**: 127.0.0.1 (localhost only)
- **Registry permissions**: 0600 (owner read/write only)
- **Key lifetime**: Session only (ephemeral)
- **Nonce reuse**: Never (random per message)
- **Forward secrecy**: Yes (ephemeral X25519 keys)

## Architecture

### Components
```
src/
├── cli/main.py              # CLI interface, argparse
├── crypto/
│   ├── box.py               # ChaCha20Poly1305 wrapper
│   └── handshake.py         # X25519 ECDH + HKDF
├── room/
│   ├── manager.py           # Room lifecycle management
│   └── registry.py          # File-based room storage
├── transport/
│   ├── socket_handler.py    # TCP + encryption layer
│   └── tor_proxy.py         # SOCKS5 proxy integration
└── utils/helpers.py         # Utility functions
```

### Threading Model
- **Main thread**: CLI I/O and user interaction
- **Accept thread**: Per host, accepts new connections
- **Handler threads**: Per client, handles messages (daemon threads)
- **Timer thread**: Per room, manages TTL expiration (daemon thread)
- **Receive thread**: Per client connection, receives messages (daemon thread)

## Room Discovery

### Local Registry
**File**: `~/.termtalk_rooms.json`  
**Format**:
```json
{
  "d0933719af4a4c89": {
    "host_ip": "192.168.1.100",
    "host_port": 12345,
    "expires_at": 1732626543.123
  }
}
```

**Limitations**:
- Process-local (same machine only)
- File-based (not suitable for distributed systems)
- No authentication on registry access
- Expired rooms cleaned up on access

**For cross-machine**: Implement distributed registry (Redis, etcd, HTTP service)

## Tor Integration

### SOCKS5 Proxy
- **Library**: PySocks
- **Default**: 127.0.0.1:9050
- **Mechanism**: Monkey-patches `socket.socket` to use `socks.socksocket`
- **DNS**: Resolved through Tor (prevents leaks)

### Activation
```python
if args.tor:
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", args.tor_port)
    socket.socket = socks.socksocket
```

### Performance Impact
- Connection setup: +1-2 seconds
- Message latency: +100-500ms
- Throughput: Limited by Tor network

## Notifications

### Visual Indicators
- `✅` Green: Success (connection, join)
- `❌` Red: Disconnection, errors
- `🔒` Cyan: Encryption status
- `🧅` Magenta: Tor mode active
- `[SECURITY]` Yellow: Security events

### Events
1. **Peer joined**: Shows IP, peer count
2. **Peer left**: Shows IP, remaining count
3. **Connection established**: Shows host:port
4. **Secure channel**: Confirms encryption active
5. **Security violations**: Rate limits, oversized messages

## Error Handling

### Connection Errors
- **Connection refused**: Tor not running, wrong IP/port
- **Timeout**: Peer unreachable, network issues
- **Invalid key**: Handshake format error

### Message Errors
- **Authentication failed**: Tampered ciphertext
- **Oversized message**: Exceeds 64 KB limit
- **Decode error**: Invalid Base64 or format

### Security Errors
- **Max connections**: Connection limit reached
- **Rate limit**: Too many rapid connections
- **Invalid input**: Malformed keys or messages

All errors logged with context but details not exposed to peers (security).

## Dependencies

### Required
- `cryptography >= 42.0.0`: Crypto primitives
- `termcolor`: Colored terminal output
- `PySocks >= 1.7.1`: Tor SOCKS5 support

### Development
- `black >= 24.0.0`: Code formatting
- `ruff >= 0.6.0`: Linting
- `unittest`: Testing (stdlib)

