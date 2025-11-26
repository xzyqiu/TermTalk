# TermTalk Security Reference - Quick Guide

## Security Controls Active

### 🔒 Connection Security

| Control | Limit | Purpose |
|---------|-------|---------|
| **Per-IP Connections** | 5 simultaneous | Prevent single attacker from monopolizing service |
| **Total Connections** | 50 simultaneous | Global resource protection |
| **Connection Rate** | 10 per minute per IP | Prevent rapid connection flooding |
| **Accept Timeout** | 30 seconds | Prevent accept() blocking forever |
| **Client Timeout** | 60 seconds | Detect and close dead connections |

### 🔐 Cryptographic Protection

- **Algorithm:** ChaCha20-Poly1305 AEAD
- **Key Exchange:** X25519 ECDH with HKDF
- **Key Size:** 256 bits
- **Nonce:** Random 96 bits (prevents replay)
- **Authentication Tag:** 128 bits (prevents tampering)
- **Forward Secrecy:** ✅ Yes (ephemeral keys)

### 📏 Input Validation

| Input | Limit | Action on Violation |
|-------|-------|---------------------|
| **Public Key** | 512 bytes max | Reject connection |
| **Message Size** | 64 KB max | Close connection |
| **Room ID** | 16 hex chars | N/A (generated) |

### 🛡️ Default Configuration

```python
# Network
Default Binding: 127.0.0.1 (localhost only)
Default Port: 12345
Max Connections: 50
Max Per IP: 5

# Room
Room ID Length: 16 characters (64 bits entropy)
Default TTL: 300 seconds (5 minutes)

# Files
Registry File: ~/.termtalk_rooms.json
Registry Permissions: 0600 (owner only)
```

## Security Warnings

### When you see these messages:

```
[SECURITY] Max connections reached, rejecting X.X.X.X
```
→ Someone is trying to open too many connections. Likely DoS attempt.

```
[SECURITY] Max connections per IP reached for X.X.X.X
```
→ Single IP hit per-IP limit. Could be legitimate if multiple clients behind NAT, or attack.

```
[SECURITY] Rate limit exceeded for X.X.X.X
```
→ Too many connection attempts in short time. Likely automated attack.

```
[SECURITY] Invalid public key length from X.X.X.X
```
→ Client sent malformed handshake. Could be buggy client or probe attempt.

```
[SECURITY] Handshake failed with X.X.X.X: ValueError
```
→ Key exchange failed. Invalid crypto material or incompatible client.

```
[SECURITY] Oversized message from X.X.X.X
```
→ Message exceeded 64 KB limit. Possible buffer overflow attempt.

## Safe Usage Guidelines

### ✅ DO:

1. **Use localhost by default** (127.0.0.1)
   - Only accessible from your machine
   - Safe for testing and local development

2. **Use LAN IP for trusted networks** (192.168.x.x)
   - Share with people on your local network
   - Behind router/firewall protection

3. **Share Room IDs securely**
   - Use encrypted channels (Signal, encrypted email)
   - Don't post Room IDs publicly
   - 16-character IDs are hard to guess but not impossible

4. **Set appropriate TTLs**
   - Short sessions: 300 seconds (5 min)
   - Longer chats: 3600 seconds (1 hour)
   - Never use very long TTLs (hours/days)

5. **Monitor security messages**
   - Watch for repeated security warnings
   - Investigate suspicious patterns
   - Stop service if under attack

### ❌ DON'T:

1. **Don't bind to 0.0.0.0 on public internet**
   - Exposes service to everyone
   - No authentication beyond Room ID
   - Risk of brute force attacks

2. **Don't share Room IDs in plaintext**
   - SMS can be intercepted
   - Unencrypted email can be read
   - Public forums are visible to all

3. **Don't ignore security warnings**
   - Multiple warnings indicate problems
   - Could be under active attack
   - Stop service and investigate

4. **Don't use for sensitive communications**
   - This is a demo/educational tool
   - Not audited for high-security use
   - Use Signal/WhatsApp for sensitive topics

5. **Don't run as root/admin**
   - Use regular user account
   - Limits damage if compromised
   - Standard security practice

## Attack Scenarios & Mitigations

### Scenario 1: Connection Flood
**Attack:** Attacker opens 100+ connections rapidly  
**Protection:** 
- Per-IP limit: Max 5 connections
- Rate limit: Max 10/minute
- Global limit: Max 50 total
**Result:** ✅ Mitigated

### Scenario 2: Slowloris (Slow Connection)
**Attack:** Attacker opens connection, sends nothing, keeps it open  
**Protection:**
- 60-second timeout on idle connections
- Automatic cleanup after timeout
**Result:** ✅ Mitigated

### Scenario 3: Oversized Message
**Attack:** Send 10 MB message to cause memory exhaustion  
**Protection:**
- 64 KB per-message limit
- Connection closed if exceeded
**Result:** ✅ Mitigated

### Scenario 4: Brute Force Room ID
**Attack:** Try random Room IDs to find active rooms  
**Protection:**
- 64 bits entropy = 18 quintillion possibilities
- Would take centuries at 1M attempts/sec
- Registry file is local (not queryable remotely)
**Result:** ✅ Mitigated (but still possible with luck)

### Scenario 5: Man-in-the-Middle
**Attack:** Intercept and modify handshake  
**Protection:**
- X25519 ECDH key exchange (MITM resistant with key verification)
- ⚠️ No key fingerprint verification implemented
- ⚠️ No certificate/PKI system
**Result:** ⚠️ Partially vulnerable (trust on first use)

### Scenario 6: Replay Attack
**Attack:** Capture and resend encrypted messages  
**Protection:**
- Random 96-bit nonces on every message
- Same plaintext → different ciphertext
- No message will decrypt twice with different nonce
**Result:** ✅ Mitigated

### Scenario 7: Message Tampering
**Attack:** Modify encrypted message in transit  
**Protection:**
- Poly1305 authentication tag (128-bit)
- Any modification causes authentication failure
- Message rejected before decryption
**Result:** ✅ Mitigated

## Monitoring & Debugging

### View active connections:
```bash
# On Linux
netstat -an | grep :12345

# Or with ss
ss -tn | grep :12345
```

### Check registry file:
```bash
cat ~/.termtalk_rooms.json
```

### Monitor security events:
```bash
# Run TermTalk and watch for [SECURITY] messages
# Redirect to log file:
python3 -m src.cli.main 2>&1 | tee termtalk.log
```

### Test security limits:
```bash
# Test per-IP connection limit (should fail after 5)
for i in {1..10}; do nc localhost 12345 & done

# Test rate limiting (should fail after 10 rapid attempts)
for i in {1..15}; do
  nc -w 1 localhost 12345 < /dev/null
  sleep 0.1
done
```

## Compliance & Audit

### Security Tests:
- 18 tests covering crypto, connections, input validation
- All tests passing ✅
- See: `tests/test_security.py`

### Documentation:
- Security Audit: `SECURITY_AUDIT.md`
- Security Fixes: `SECURITY_FIXES.md`
- This Guide: `SECURITY_REFERENCE.md`
- Threat Model: `docs/threat_model.md`

### Known Limitations:
1. No MITM protection without key fingerprint verification
2. Room IDs could be guessed with extreme luck
3. Metadata (IP, timing) not protected (no TLS)
4. No persistent authentication (rooms are ephemeral)
5. File-based registry is local-only

---

**Last Updated:** November 26, 2025  
**Version:** Post-security-fixes  
**Security Status:** 🟢 Suitable for trusted networks
