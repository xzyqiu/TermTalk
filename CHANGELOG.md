# Changelog

All notable changes to TermTalk are documented in this file.

## [2.0.1] - 2025-12-18

### 🌐 Network Connectivity Improvements

#### Added
- **Direct IP connection mode** for LAN/Internet connectivity
  - When Room ID not found in local registry, prompts for host IP:port
  - Enables internet connections without shared registry file
  - Supports localhost, LAN, and internet (with port forwarding)

#### Documentation
- Added comprehensive "Network Connectivity" section to README
  - Localhost, LAN, and Internet setup instructions
  - Port forwarding guide for internet hosting
  - Security recommendations for each network mode
  - Practical examples with IP addresses

#### Fixed
- Clarified that registry is local-only, but connections work over any network
- Added workaround instructions for cross-network communication

## [2.0.0] - 2025-11-26 (Updated 2025-12-18)

### 🔐 Security - Major Cryptographic Upgrade

#### Added
- **ChaCha20-Poly1305 AEAD encryption** replacing HMAC-only approach
  - 256-bit keys, 96-bit random nonces, 128-bit authentication tags
  - Provides both confidentiality and integrity
  - Prevents tampering and ensures replay protection

- **X25519 ECDH key exchange** replacing insecure string concatenation
  - Elliptic curve Diffie-Hellman for secure key agreement
  - HKDF-SHA256 for proper key derivation with domain separation
  - Ephemeral keys provide forward secrecy
  - Each session generates new key pair

#### Security Improvements
- Changed default binding from `0.0.0.0` to `127.0.0.1` (localhost only)
- Added security warnings for public interface binding
- Increased Room ID entropy from 32 to 64 bits (8 → 16 characters)
- Set restrictive file permissions on registry (0600 - owner only)

### 🕵️ Privacy Protection (2025-12-18)

#### Added
- **Ephemeral ID generation** using cryptographically secure randomness
  - Room IDs: 16-character hex strings from `secrets.token_bytes(8)` (64-bit entropy)
  - Peer IDs: 6-character alphanumeric strings from `secrets.choice()` 
  - No MAC addresses, hostnames, or system metadata exposed

- **Privacy protection module** (`src/utils/privacy.py`)
  - `generate_anonymous_room_id()`: MAC-address-free room identifiers
  - `generate_anonymous_peer_id()`: System-independent peer identifiers
  - `sanitize_error_message()`: Removes filesystem paths from errors
  - `get_privacy_info()`: Privacy status reporting

- **Error message sanitization** to prevent information leakage
  - Strips filesystem paths, usernames, system paths
  - Only returns error type (e.g., "ValueError") without sensitive details

- **Privacy status display** in CLI
  - Shows "🔒 Privacy: Ephemeral IDs only (no MAC, hostname, or system info exposed)"
  - Confirms no persistent identifiers being used

#### Removed
- `uuid.uuid4()` usage replaced with `secrets`-based generation
  - Prevents potential MAC address exposure from uuid1 fallback
  - Ensures cryptographically secure randomness

#### Testing
- Added 12 privacy tests (`tests/test_privacy.py`)
  - Verifies no MAC addresses in IDs
  - Checks for forbidden imports (platform, gethostname, uuid.getnode)
  - Validates ID randomness (100+ unique samples)
  - Tests error message sanitization
  - Confirms registry contains only ephemeral data

### 🛡️ DoS Protection & Rate Limiting

#### Added
- **Connection limits**: Maximum 5 connections per IP, 50 global
- **Rate limiting**: Maximum 10 new connections per minute per IP
- **Socket timeouts**: 30s accept timeout, 60s client timeout
- **SO_REUSEADDR**: Socket reuse for quick service restart
- **Input validation**: 512-byte key limit, 64KB message limit
- **Connection tracking**: Per-IP connection counting with cleanup

### 🧅 Tor Integration

#### Added
- `--tor` command-line flag for anonymous routing
- `--tor-port` option for custom Tor SOCKS5 port (default: 9050)
- PySocks integration for transparent SOCKS5 proxying
- Tor status indicator (🧅) in UI
- Comprehensive Tor documentation (`docs/TOR_GUIDE.md`)

### 🔔 User Experience Improvements

#### Added
- **Real-time notifications**:
  - ✅ Green notification when peer joins (shows IP and peer count)
  - ❌ Red notification when peer leaves (shows remaining count)
  - ✅ Green notification on successful connection
  - 🔒 Cyan indicator for secure encrypted channel
- **Colored terminal output** using termcolor
- **Command-line argument parsing** with argparse
- **Better error messages** with specific exception handling

### 📊 Testing & Quality

#### Added
- `tests/test_security.py` with 11 new security tests:
  - Connection flooding tests
  - Incomplete handshake handling
  - Invalid peer key rejection
  - Oversized message handling
  - Malformed message rejection
  - Replay attack detection
  - Message tampering detection
  - Wrong key decryption tests
  - Special character handling
  - Empty message handling
- Total test count: 18 comprehensive tests
- All tests passing ✅

### 📚 Documentation

#### Added
- `SECURITY_AUDIT.md`: Comprehensive vulnerability assessment (11 issues identified)
- `SECURITY_FIXES.md`: Detailed changelog of security improvements
- `SECURITY_REFERENCE.md`: Quick reference for security features
- `docs/TOR_GUIDE.md`: Complete Tor integration guide
- `CHANGELOG.md`: This file

#### Updated
- `README.md`: Reflects all new features, security controls, and Tor support
- `docs/spec.md`: Complete technical specification with crypto details
- `docs/threat_model.md`: Updated threat analysis with mitigation status
- All documentation now reflects post-security-hardening state

### 🔧 Technical Changes

#### Modified Files
- `src/crypto/box.py`: Replaced with ChaCha20-Poly1305 implementation
- `src/crypto/handshake.py`: Replaced with X25519 ECDH + HKDF
- `src/transport/socket_handler.py`: Added security controls and notifications
- `src/cli/main.py`: Added argparse, Tor support, security warnings
- `src/room/manager.py`: Increased Room ID length to 16 characters
- `src/room/registry.py`: Added file permission setting (0600)
- `requirements.txt`: Added `PySocks>=1.7.1` for Tor support

#### New Files
- `src/transport/tor_proxy.py`: Tor SOCKS5 proxy integration module
- `tests/test_security.py`: Security-focused test suite

### 🐛 Bug Fixes
- Fixed potential resource leaks from incomplete handshakes
- Fixed missing cleanup on connection failures
- Added proper exception handling throughout codebase
- Fixed race conditions in connection tracking

### ⚠️ Breaking Changes
- **Default binding changed**: Now binds to `127.0.0.1` instead of `0.0.0.0`
  - Users wanting LAN access must explicitly enter their IP
- **Room ID format**: Changed from 8 to 16 characters
  - Old 8-character Room IDs will not work
- **Crypto protocol**: Completely replaced
  - Not backward compatible with old HMAC-based protocol
  - Clients must use same version to communicate

### 📈 Performance Impact
- Slightly increased handshake time due to X25519 computation (~10-20ms)
- ChaCha20 encryption is faster than AES on most CPUs
- Connection limiting may reject legitimate users under heavy load
- Tor mode adds 1-2 seconds per connection establishment

### 🎯 Security Scorecard

| Category | Before | After | Change |
|----------|--------|-------|--------|
| **Cryptography** | 🟡 5/10 | 🟢 9/10 | +4 |
| **Network Security** | 🔴 3/10 | 🟢 8/10 | +5 |
| **Input Validation** | 🟡 6/10 | 🟢 8/10 | +2 |
| **Authentication** | 🟡 4/10 | 🟡 6/10 | +2 |
| **DoS Protection** | 🔴 2/10 | 🟢 8/10 | +6 |
| **Configuration** | 🔴 3/10 | 🟢 8/10 | +5 |
| **Error Handling** | 🟡 5/10 | 🟢 7/10 | +2 |
| **Overall** | 🔴 4.6/10 | 🟢 7.7/10 | **+3.1** |

### 🔮 Future Considerations
- Add key fingerprint verification for MITM detection
- Implement room passwords for additional authentication
- Add host controls (kick, ban functionality)
- Message padding to prevent traffic analysis
- Distributed registry for cross-machine discovery
- Support for .onion hidden services

---

## [1.0.0] - Initial Release (Pre-Security-Audit)

### Features
- Basic P2P terminal chat
- HMAC-SHA256 message authentication (no encryption)
- Simple string concatenation "key exchange"
- Ephemeral rooms with TTL
- File-based room registry
- Basic CLI interface

### Known Issues (Fixed in 2.0.0)
- 🔴 No encryption (only HMAC)
- 🔴 Insecure key derivation
- 🔴 Default binding to 0.0.0.0
- 🔴 No connection limits
- 🔴 No rate limiting
- 🔴 No socket timeouts
- 🟠 Weak Room ID entropy (32 bits)
- 🟡 World-readable registry file

---

## Version History

- **2.0.0** (2025-11-26, updated 2025-12-18): Security hardening, Tor support, privacy protection, comprehensive improvements
- **1.0.0** (Initial): Basic functionality, known security issues

---

## 📚 Documentation

New in v2.0.0:
- **SECURITY_AUDIT.md**: Comprehensive vulnerability assessment
- **SECURITY_FIXES.md**: Detailed security improvements
- **SECURITY_REFERENCE.md**: Quick security controls reference
- **docs/threat_model.md**: Threat analysis and mitigations
- **docs/TOR_GUIDE.md**: Tor integration guide
- **docs/PRIVACY.md** (2025-12-18): Privacy protections and guarantees
- **docs/INDEX.md**: Documentation index

---

**Deployment Recommendation:**
- v1.0.0: 🔴 **Not production ready**
- v2.0.0: 🟢 **Suitable for trusted networks**
