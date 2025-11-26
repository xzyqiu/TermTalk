# Security Audit Report - TermTalk
**Date:** November 26, 2025  
**Version:** Current (main branch)  
**Auditor:** Security Review

## Executive Summary

This audit identifies critical and moderate security vulnerabilities in the TermTalk peer-to-peer messaging application. While the cryptographic primitives have been upgraded to industry standards (ChaCha20-Poly1305, X25519), several configuration and implementation issues expose the system to attacks.

**Risk Level:** 🔴 HIGH (Production deployment not recommended without fixes)

---

## Critical Vulnerabilities

### 1. 🔴 CRITICAL: Default Binding to 0.0.0.0 (All Interfaces)
**Location:** `src/cli/main.py:16`  
**Risk:** Remote exploitation, unauthorized access

```python
host_ip = input("Enter your IP to host (0.0.0.0 for all interfaces): ").strip() or "0.0.0.0"
```

**Issue:**
- Defaults to binding on ALL network interfaces including public IPs
- Users may not understand the security implications
- Exposes chat service to internet without warning

**Impact:**
- Anyone on the internet can connect to the host
- Room IDs could be brute-forced (only 8 hex chars = 32 bits)
- No authentication beyond shared room discovery

**Recommendation:**
- Default to `127.0.0.1` (localhost only)
- Require explicit opt-in for public binding with security warning
- Add `--bind-all` flag with clear documentation

---

### 2. 🔴 CRITICAL: No Connection Rate Limiting
**Location:** `src/transport/socket_handler.py:28-33`  
**Risk:** Denial of Service (DoS)

```python
def _accept_loop(self) -> None:
    while self.running:
        try:
            conn, addr = self.sock.accept()
        except OSError:
            break
```

**Issue:**
- Unlimited connection acceptance
- No rate limiting or throttling
- No maximum connection count
- Each connection spawns a thread (resource exhaustion)

**Impact:**
- Attacker can exhaust system resources (file descriptors, memory, CPU)
- 1000+ connections can crash the host
- No protection against SYN flood or connection spam

**Recommendation:**
- Implement per-IP connection limits (e.g., max 5 connections per IP)
- Add global connection limit (e.g., max 50 total connections)
- Add connection rate limiting (e.g., max 10 new connections per minute per IP)
- Use connection timeouts for idle connections

---

### 3. 🔴 CRITICAL: No Socket Timeouts
**Location:** `src/transport/socket_handler.py` (multiple locations)  
**Risk:** Resource exhaustion, hanging connections

**Issue:**
- `recv()` calls block indefinitely
- No timeout on socket operations
- Incomplete handshakes can hang forever
- Idle connections never close

**Impact:**
- Slowloris-style attacks (open connections, send nothing)
- Resource leaks from abandoned connections
- Cannot detect dead peers

**Recommendation:**
```python
sock.settimeout(30)  # 30-second timeout
conn.settimeout(60)  # 60-second timeout for established connections
```

---

### 4. 🟠 HIGH: No Handshake Timeout or Retry Limit
**Location:** `src/transport/socket_handler.py:38-42`  
**Risk:** Brute force attacks, resource exhaustion

```python
handshake = Handshake()
conn.sendall((handshake.get_public_key_str() + "\n").encode())
peer_pub_key = conn.recv(1024).decode().strip()
secure_box = SecureBox(handshake.generate_shared_box(peer_pub_key))
```

**Issue:**
- No limit on handshake attempts
- Invalid public keys cause exceptions but connection retains resources
- No exponential backoff or IP blocking

**Impact:**
- Attacker can repeatedly attempt invalid handshakes
- Can test for vulnerabilities in key validation
- Resource consumption from failed handshakes

**Recommendation:**
- Add 3-attempt limit per connection
- Implement exponential backoff
- Track failed attempts per IP address
- Close connection after repeated failures

---

## Moderate Vulnerabilities

### 5. 🟠 MODERATE: Weak Room ID Entropy
**Location:** `src/room/manager.py:13`  
**Risk:** Brute force enumeration

```python
self.room_id = str(uuid.uuid4())[:8]  # Only 8 hex chars
```

**Issue:**
- Only 32 bits of entropy (4.3 billion possibilities)
- Can be brute-forced in hours with modern hardware
- Sequential scanning can discover active rooms

**Impact:**
- Unauthorized users can join private rooms
- Room discovery without host permission
- Privacy violation

**Recommendation:**
- Increase to 16+ characters (64+ bits entropy)
- Use cryptographically secure random generation
- Add optional password protection for rooms

---

### 6. 🟠 MODERATE: No Input Length Validation
**Location:** `src/transport/socket_handler.py:46-47`  
**Risk:** Memory exhaustion, buffer overflow

```python
data = conn.recv(4096)
```

**Issue:**
- Receives up to 4096 bytes but no accumulated message size limit
- Attacker can send infinite small messages
- No validation of message size before decryption

**Impact:**
- Memory exhaustion from accumulated messages
- Processing overhead from oversized encrypted payloads

**Recommendation:**
- Add per-message size limit (e.g., 64 KB)
- Track cumulative received data per connection
- Reject oversized messages before decryption

---

### 7. 🟠 MODERATE: Information Disclosure in Error Messages
**Location:** `src/transport/socket_handler.py:52-53`  
**Risk:** Information leakage

```python
except Exception:
    print(f"[{peer_id}] Received corrupted message")
```

**Issue:**
- Generic error messages hide specific failure reasons
- No distinction between decryption failure, timeout, etc.
- May aid attackers in understanding system behavior

**Impact:**
- Low - mainly operational concern
- Could help attackers fingerprint the system

**Recommendation:**
- Log detailed errors server-side
- Send generic errors to clients
- Implement structured logging with severity levels

---

### 8. 🟡 LOW: Missing SO_REUSEADDR
**Location:** `src/transport/socket_handler.py:19`  
**Risk:** Service availability

**Issue:**
- Socket not configured with `SO_REUSEADDR`
- Cannot restart service quickly after crash
- "Address already in use" errors

**Recommendation:**
```python
self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

---

### 9. 🟡 LOW: File-Based Registry World-Readable
**Location:** `src/room/registry.py:19`  
**Risk:** Information disclosure

```python
registry_path = os.path.join(os.path.expanduser("~"), ".termtalk_rooms.json")
```

**Issue:**
- File created with default permissions (likely 644)
- Other users on system can read room information
- Contains IP addresses and ports

**Recommendation:**
```python
os.chmod(self.registry_path, 0o600)  # Owner read/write only
```

---

## Configuration Issues

### 10. No TLS/Transport Encryption
**Status:** By design for P2P, but risky

While E2E encryption is implemented, the lack of TLS means:
- Metadata visible (IP addresses, timing, packet sizes)
- Traffic analysis possible
- No protection against MITM during handshake

**Recommendation:** Document this limitation clearly

---

### 11. No Authentication/Authorization
**Status:** By design, but exploitable

- Anyone with Room ID can join
- No password protection
- No participant limit
- No host controls (kick, ban)

**Recommendation:** Add optional room passwords

---

## Test Results

Security tests created in `tests/test_security.py` validate:

✅ **Passed:**
- Authentication failures detected correctly
- Tampered ciphertexts rejected
- Wrong key decryption fails
- Replay protection (random nonces)
- Special character handling
- Invalid input rejection
- Oversized message handling

⚠️ **Warnings:**
- Connection flooding causes resource issues (expected)
- Incomplete handshakes generate exceptions (needs error handling)

---

## Remediation Priority

### Immediate (Deploy blockers):
1. Change default binding from 0.0.0.0 to 127.0.0.1
2. Add socket timeouts (30-60 seconds)
3. Implement connection limits (per-IP and global)

### High Priority:
4. Add rate limiting for connections
5. Increase Room ID entropy
6. Add handshake attempt limits

### Medium Priority:
7. Implement message size validation
8. Add SO_REUSEADDR socket option
9. Improve error handling and logging

### Low Priority:
10. Fix file permissions on registry
11. Add optional room passwords
12. Document metadata leakage risks

---

## Security Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Cryptography** | 🟢 9/10 | Excellent after recent fixes |
| **Network Security** | 🔴 3/10 | Critical issues present |
| **Input Validation** | 🟡 6/10 | Basic validation, needs limits |
| **Authentication** | 🟡 4/10 | Weak room discovery |
| **DoS Protection** | 🔴 2/10 | Highly vulnerable |
| **Configuration** | 🔴 3/10 | Dangerous defaults |
| **Error Handling** | 🟡 5/10 | Needs improvement |
| **Overall** | 🔴 4.6/10 | **Not production ready** |

---

## Conclusion

TermTalk has **strong cryptographic foundations** but **critical deployment vulnerabilities**. The application should NOT be deployed to production or exposed to untrusted networks until at least the "Immediate" priority items are addressed.

The most dangerous issue is the **default binding to 0.0.0.0**, which could expose users to attacks without their knowledge.

**Recommendation:** Implement immediate fixes before any public release.
