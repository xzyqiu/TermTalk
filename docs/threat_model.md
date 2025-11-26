# Threat Model — TermTalk

**Version**: 2.0 (Post-Security-Hardening)  
**Date**: November 26, 2025  
**Status**: Suitable for trusted networks

## Summary
TermTalk is a secure, terminal-based peer-to-peer chat system with strong cryptography and hardened security controls. This threat model documents assets, threat actors, attack vectors, and mitigations implemented after comprehensive security audit.

## Assets

### Critical Assets
1. **Message Confidentiality**: Chat content must remain private
2. **Session Keys**: Ephemeral X25519 private keys and derived ChaCha20 keys
3. **Message Integrity**: Prevention of tampering or forgery
4. **User Anonymity** (with Tor): IP address and location privacy

### Important Assets
5. **Room IDs**: 16-character identifiers for room access
6. **Service Availability**: Host's ability to accept connections
7. **Registry Data**: Room metadata in ~/.termtalk_rooms.json

### Less Critical Assets
8. **Metadata**: Connection timing, message sizes, frequency
9. **Public Keys**: X25519 public keys (non-sensitive by design)

## Assumptions

### Trust Boundaries
- ✅ Users control their endpoint devices
- ✅ Operating system and Python runtime are not compromised
- ✅ Network path is untrusted (adversary can observe/modify traffic)
- ✅ Peers may be malicious (Byzantine fault model)

### Operational Environment
- 🏠 Designed for: Trusted networks (home LANs, development environments)
- ⚠️ Acceptable for: Semi-trusted networks with Tor enabled
- 🚫 Not for: Production use, high-security environments, public internet without Tor

### Cryptographic Assumptions
- Standard cryptographic assumptions (DH, AEAD security)
- Hardware RNG (`os.urandom`) provides sufficient entropy
- No quantum adversary (X25519 not post-quantum secure)

## Threat Actors

| Actor | Capability | Motivation |
|-------|------------|------------|
| **Script Kiddie** | Automated tools, public exploits | Disruption, learning |
| **Network Observer** | Passive traffic monitoring | Surveillance, data collection |
| **Active Attacker** | Traffic modification, DoS | Disruption, data theft |
| **Malicious Peer** | Valid room access | Spam, harassment, data mining |
| **Nation State** (out of scope) | Global surveillance | Intelligence gathering |

## Threats & Mitigations

### 1. Network Eavesdropping ⚠️→✅
**Threat**: Passive adversary captures and analyzes network traffic  
**Impact**: Message content exposure, metadata leakage  
**Mitigations**:
- ✅ **ChaCha20-Poly1305 AEAD**: All messages encrypted with 256-bit keys
- ✅ **Random nonces**: 96-bit nonces prevent pattern analysis
- ✅ **Tor support**: `--tor` flag hides IP addresses and routes
- ⚠️ **Residual**: Metadata (timing, size) still observable without Tor

**Status**: ✅ **MITIGATED** (with encryption) / 🟡 **PARTIAL** (metadata)

---

### 2. Man-in-the-Middle (MITM) Attack ⚠️→🟡
**Threat**: Adversary intercepts and modifies handshake to impersonate peers  
**Impact**: Complete compromise of session confidentiality/integrity  
**Mitigations**:
- ✅ **X25519 ECDH**: Secure key agreement resistant to passive MITM
- ⚠️ **No key verification**: Lacks fingerprint comparison (trust-on-first-use)
- 🟡 **Room ID as weak auth**: Adversary needs Room ID to intercept

**Status**: 🟡 **PARTIALLY MITIGATED** (requires out-of-band key verification)

---

### 3. Denial of Service (DoS) 🔴→✅
**Threat**: Attacker floods host with connections or messages  
**Impact**: Service unavailability, resource exhaustion  
**Mitigations**:
- ✅ **Connection limits**: 5 per IP, 50 global
- ✅ **Rate limiting**: 10 connections/min per IP
- ✅ **Socket timeouts**: 30-60 seconds prevent hanging
- ✅ **Message size limits**: 64 KB maximum
- ✅ **Input validation**: Reject malformed keys/messages

**Status**: ✅ **MITIGATED** (comprehensive controls)

---

### 4. Message Tampering 🔴→✅
**Threat**: Adversary modifies encrypted messages in transit  
**Impact**: Corrupted messages, potential exploitation  
**Mitigations**:
- ✅ **Poly1305 MAC**: 128-bit authentication tag
- ✅ **AEAD**: Encrypt-then-MAC prevents tampering
- ✅ **Immediate rejection**: Failed auth = drop message

**Status**: ✅ **MITIGATED** (cryptographic authentication)

---

### 5. Replay Attacks 🔴→✅
**Threat**: Adversary captures and resends old messages  
**Impact**: Duplicate messages, confusion, potential exploit  
**Mitigations**:
- ✅ **Random nonces**: 96-bit nonce per message
- ✅ **Different ciphertexts**: Same plaintext → different ciphertext
- ⚠️ **No sequence numbers**: Very old replays theoretically possible

**Status**: ✅ **MITIGATED** (nonce randomization prevents practical replay)

---

### 6. Room ID Brute Force 🟡→🟢
**Threat**: Adversary guesses Room IDs to join unauthorized  
**Impact**: Unauthorized access to private conversations  
**Mitigations**:
- ✅ **64-bit entropy**: 2^64 = 18 quintillion possibilities
- ✅ **Short TTL**: Rooms expire after 5 minutes (default)
- ✅ **Local registry**: No remote enumeration API
- 🟡 **Weak password alternative**: No optional password protection

**Status**: 🟢 **LOW RISK** (computationally infeasible in room lifetime)

---

### 7. Malicious Peer Behavior 🟡→🟡
**Threat**: Legitimate peer sends spam, exploits, or harassment  
**Impact**: Degraded user experience, potential system exploitation  
**Mitigations**:
- ✅ **Input validation**: Size limits, format checks
- ✅ **Message authentication**: Can't forge host messages
- ⚠️ **No host controls**: Can't kick or ban peers
- ⚠️ **No content filtering**: Malicious content passes through

**Status**: 🟡 **PARTIALLY MITIGATED** (technical controls only)

---

### 8. Host Compromise 🔴→🔴
**Threat**: Attacker gains access to host machine memory  
**Impact**: Session key extraction, message decryption  
**Mitigations**:
- ✅ **Ephemeral keys**: Keys exist only during session
- ✅ **No persistence**: Keys never written to disk
- ⚠️ **Memory access**: Keys in RAM if attacker has access
- 🔴 **No secure enclave**: Standard Python memory management

**Status**: 🔴 **UNMITIGATED** (architectural limitation)

---

### 9. Traffic Analysis 🟡→🟡
**Threat**: Adversary correlates timing/size patterns without decryption  
**Impact**: Metadata leakage, participant identification  
**Mitigations**:
- 🟢 **Tor support**: `--tor` flag for network-level anonymity
- ⚠️ **No padding**: Message sizes reveal plaintext lengths
- ⚠️ **No timing obfuscation**: Send times reveal activity patterns

**Status**: 🟡 **PARTIALLY MITIGATED** (Tor helps, but not perfect)

---

### 10. Software Vulnerabilities 🟡→🟢
**Threat**: Bugs in code allow exploitation  
**Impact**: Varies (DoS, info leak, RCE in worst case)  
**Mitigations**:
- ✅ **Comprehensive tests**: 18 unit + security tests
- ✅ **Input validation**: All external input validated
- ✅ **Safe libraries**: `cryptography` library (audited)
- ✅ **Exception handling**: Graceful failure modes
- 🟡 **No fuzzing**: No systematic fuzzing performed

**Status**: 🟢 **ACCEPTABLE** (good practices, but not formally verified)

---

## Security Scorecard (Updated)

| Threat | Before Audit | After Fixes | Status |
|--------|--------------|-------------|--------|
| Eavesdropping | 🔴 Plaintext | ✅ ChaCha20 | **Fixed** |
| MITM | 🔴 No auth | 🟡 ECDH only | **Improved** |
| DoS | 🔴 No limits | ✅ Multi-layer | **Fixed** |
| Tampering | 🟠 HMAC only | ✅ AEAD | **Fixed** |
| Replay | 🔴 None | ✅ Nonces | **Fixed** |
| Brute Force | 🟠 32-bit | 🟢 64-bit | **Fixed** |
| Malicious Peer | 🟡 Minimal | 🟡 Basic | **Same** |
| Host Compromise | 🔴 Vulnerable | 🔴 Vulnerable | **Unfixable** |
| Traffic Analysis | 🔴 Exposed | 🟡 Tor option | **Improved** |
| Software Bugs | 🟡 Untested | 🟢 Tested | **Improved** |

**Overall**: 🟢 **7/10** suitable for trusted networks

---

## Residual Risks

### High Priority
1. **No MITM detection**: Consider key fingerprint verification UI
2. **No host controls**: Add kick/ban functionality
3. **Memory compromise**: Document limitation clearly

### Medium Priority
4. **Traffic analysis**: Consider message padding
5. **Room passwords**: Add optional authentication layer
6. **Distributed registry**: File-based limits scalability

### Low Priority
7. **Message sequence numbers**: Prevent very old replays
8. **Fuzzing**: Systematic input fuzzing for robustness
9. **Formal audit**: Professional security audit for production

---

## Recommendations by Use Case

### ✅ Acceptable Use
- Development and testing environments
- Trusted home/office LANs
- Educational demonstrations
- Short-lived coordination (< 5 minutes)

### 🟡 Use with Caution
- Semi-trusted networks (use `--tor`)
- Longer sessions (consider MITM risk)
- Public WiFi (definitely use `--tor`)

### 🔴 Not Recommended
- Production services
- Sensitive communications (use Signal/WhatsApp)
- High-security requirements
- Long-term communications
- Untrusted or hostile networks without Tor

