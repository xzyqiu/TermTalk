# TermTalk Privacy Protection

TermTalk is designed with privacy-first principles to ensure users cannot be tracked or identified through persistent identifiers or system metadata.

## Privacy Guarantees

### ✅ No MAC Address Exposure
- **Never uses `uuid.uuid1()`** which embeds hardware MAC addresses
- All identifiers use cryptographically secure randomness (`secrets` module)
- Room IDs: 16-character hex strings (64-bit entropy) from `secrets.token_bytes(8)`
- Peer IDs: 6-character alphanumeric strings from `secrets.choice()`

### ✅ No Hostname Leakage
- **Never calls `socket.gethostname()`** or similar functions
- No hostnames transmitted in handshakes, messages, or registry
- Only IP addresses and ports stored (ephemeral session data)

### ✅ No System Metadata
- **Does not use `platform` module** for OS/Python version detection
- No username exposure (`os.getlogin()`, `os.environ['USER']`)
- Error messages sanitized to remove filesystem paths
- No disk serial numbers or hardware identifiers

### ✅ Ephemeral Identifiers Only
- All Room IDs expire after TTL (default: 5 minutes)
- Peer IDs are session-only, not persisted
- Registry file contains only: `room_id`, `host_ip`, `host_port`, `expires_at`
- No long-term tracking possible across sessions

### ✅ Cryptographically Secure Randomness
- Uses `secrets` module (not `random`) for all ID generation
- Session IDs: 32 random bytes per process
- Room/Peer IDs generated independently with high entropy

## Privacy Best Practices

### Maximum Privacy Mode
```bash
# Use Tor to hide IP address
python3 -m src.cli.main --tor

# Use short TTLs (room expires quickly)
python3 -m src.cli.main host --ttl 300  # 5 minutes

# Clear registry after sensitive sessions
rm /tmp/termtalk_rooms.json
```

### What TermTalk Does NOT Collect
- ❌ MAC addresses
- ❌ Hostnames or computer names
- ❌ Usernames
- ❌ Operating system information
- ❌ Python version
- ❌ Filesystem paths
- ❌ Hard drive serial numbers
- ❌ System uptime or process information

### What TermTalk DOES Store (Temporarily)
- ✅ Room IDs (ephemeral, expire after TTL)
- ✅ IP addresses (for connections, cleared on disconnect)
- ✅ Port numbers (for connections)
- ✅ Expiration timestamps (for room cleanup)

**All stored data is session-only and automatically deleted.**

## Privacy Architecture

### Anonymous ID Generation
```python
# Room ID: 64-bit entropy, no MAC address
room_id = secrets.token_bytes(8).hex()  # e.g., "a3f5d7b9e2c4f6a8"

# Peer ID: 6 random alphanumeric chars
alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
peer_id = "".join(secrets.choice(alphabet) for _ in range(6))  # e.g., "x7k2p9"
```

### Error Sanitization
```python
# Before: "/home/user/TermTalk/src/crypto/box.py: ValueError: Invalid key"
# After:  "ValueError"

sanitized = sanitize_error_message(error)  # Strips filesystem paths
```

### Registry Privacy
```json
{
  "a3f5d7b9e2c4f6a8": {
    "host_ip": "127.0.0.1",
    "host_port": 9999,
    "expires_at": 1734567890.123
  }
}
```
**File permissions: 0600 (owner read/write only)**

## Privacy Testing

Run privacy tests to verify no identifiers leak:
```bash
python3 -m unittest tests.test_privacy -v
```

Tests verify:
- ✅ No MAC addresses in Room/Peer IDs
- ✅ No `uuid.uuid1()` usage
- ✅ No `socket.gethostname()` calls
- ✅ No `platform` module imports
- ✅ Sufficient ID randomness (100+ unique samples)
- ✅ Error messages sanitized
- ✅ Registry contains only ephemeral data

## Threat Model Considerations

### What Privacy Protections Cover
1. **Local System Privacy**: No system metadata leaked from your computer
2. **Cross-Session Privacy**: Cannot correlate identities across different sessions
3. **Filesystem Privacy**: Error messages don't reveal file paths

### What Privacy Protections Do NOT Cover
1. **IP Address Privacy**: Your IP is visible to peers (use `--tor` flag to mitigate)
2. **Traffic Analysis**: Message timing and sizes are visible (standard for E2EE)
3. **Malicious Peers**: Cannot prevent peers from recording Room IDs (but they expire)

### Additional Recommendations
- **Use Tor** (`--tor` flag) to hide your IP address from peers
- **Use VPN** for additional network-level privacy
- **Short TTLs** minimize exposure window for Room IDs
- **Avoid reusing Room IDs** (each session generates new random ID)
- **Clear registry** after sensitive sessions

## Compliance with Privacy Standards

TermTalk's privacy architecture aligns with:
- **GDPR Principles**: No personal data collection, data minimization
- **Privacy by Design**: Default settings maximize privacy
- **Transparency**: Full disclosure of what is/isn't private

## Privacy Disclosure

**What we guarantee:**
- No persistent identifiers tied to your hardware
- No system metadata exposure
- Ephemeral session data only

**What we don't control:**
- Your network provider can see you're using TermTalk (use Tor)
- Peers can see your IP address (use Tor)
- Peers can log Room IDs during active session (but they expire)

---

**Privacy Status Check:**
```bash
python3 -m src.cli.main host
# Output includes: 🔒 Privacy: Ephemeral IDs only (no MAC, hostname, or system info exposed)
```

For security concerns, see [SECURITY_REFERENCE.md](SECURITY_REFERENCE.md)  
For Tor integration, see [TOR_GUIDE.md](TOR_GUIDE.md)
