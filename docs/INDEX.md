# Documentation Index

Welcome to TermTalk's documentation! This index helps you find the right document for your needs.

## 📖 Getting Started

**Start here:**
- **[README.md](../README.md)** - Project overview, quickstart, features, and basic usage

## 🔐 Security Documentation

**For security-conscious users:**
1. **[SECURITY_AUDIT.md](../SECURITY_AUDIT.md)** - Detailed vulnerability assessment (11 issues analyzed)
2. **[SECURITY_FIXES.md](../SECURITY_FIXES.md)** - Complete record of security improvements
3. **[SECURITY_REFERENCE.md](../SECURITY_REFERENCE.md)** - Quick security controls reference

**Threat modeling:**
- **[docs/threat_model.md](threat_model.md)** - Comprehensive threat analysis with mitigations

## 🛠️ Technical Documentation

**For developers and advanced users:**
- **[docs/spec.md](spec.md)** - Complete technical specification
  - Protocol flow
  - Cryptographic details
  - Architecture overview
  - Message formats

## 🌐 Network & Connectivity

**For internet and network setup:**
- **[docs/INTERNET_CONNECTIVITY.md](INTERNET_CONNECTIVITY.md)** - Complete internet connectivity guide
  - Localhost, LAN, and internet setup
  - Port forwarding instructions
  - NAT traversal solutions
  - Direct IP connection mode
  - Troubleshooting connection issues

## 🧅 Privacy & Anonymity

**For privacy-focused users:**
- **[docs/PRIVACY.md](PRIVACY.md)** - Privacy protections and guarantees
  - No MAC address, hostname, or system info exposure
  - Ephemeral identifiers only
  - Privacy best practices
  - Compliance considerations
- **[docs/TOR_GUIDE.md](TOR_GUIDE.md)** - Complete Tor integration guide
  - Installation instructions
  - Usage examples
  - Security considerations
  - Performance impact
  - Troubleshooting

## 📝 Project History

**For contributors and maintainers:**
- **[CHANGELOG.md](../CHANGELOG.md)** - Version history and changes
- **[LICENSE](../LICENSE)** - Project license

## 🎯 Quick Links by Use Case

### "I want to use TermTalk securely"
1. Read [README.md](../README.md) - Quickstart section
2. Review [SECURITY_REFERENCE.md](../SECURITY_REFERENCE.md) - Security controls
3. Check [PRIVACY.md](PRIVACY.md) - Privacy protections
4. Follow [TOR_GUIDE.md](TOR_GUIDE.md) if using on untrusted networks

### "I want to understand the security"
1. Read [SECURITY_AUDIT.md](../SECURITY_AUDIT.md) - What was vulnerable
2. Read [SECURITY_FIXES.md](../SECURITY_FIXES.md) - What was fixed
3. Review [threat_model.md](threat_model.md) - Threat analysis

### "I want to develop/contribute"
1. Read [README.md](../README.md) - Setup and testing
2. Review [spec.md](spec.md) - Technical specification
3. Check [CHANGELOG.md](../CHANGELOG.md) - Recent changes

### "I want to deploy in production"
**⚠️ Not recommended!** But if you must:
1. Read [SECURITY_AUDIT.md](../SECURITY_AUDIT.md) - Understand limitations
2. Review [threat_model.md](threat_model.md) - Residual risks
3. Implement recommendations in audit
4. Consider professional security audit

## 📊 Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| README.md | ✅ Current | 2025-12-18 |
| SECURITY_AUDIT.md | ✅ Current | 2025-11-26 |
| SECURITY_FIXES.md | ✅ Current | 2025-11-26 |
| SECURITY_REFERENCE.md | ✅ Current | 2025-11-26 |
| CHANGELOG.md | ✅ Current | 2025-11-26 |
| docs/spec.md | ✅ Current | 2025-11-26 |
| docs/threat_model.md | ✅ Current | 2025-11-26 |
| docs/TOR_GUIDE.md | ✅ Current | 2025-11-26 |
| docs/PRIVACY.md | ✅ Current | 2025-12-18 |

## 🔍 Quick Reference

### Key Features
- **Encryption**: ChaCha20-Poly1305 AEAD (256-bit)
- **Key Exchange**: X25519 ECDH + HKDF-SHA256
- **Forward Secrecy**: ✅ Yes (ephemeral keys)
- **Privacy**: ✅ No MAC address, hostname, or system info
- **Connection Limits**: 5 per IP, 50 global
- **Rate Limiting**: 10/min per IP
- **Room ID**: 16 hex chars (64-bit entropy)
- **Tor Support**: ✅ Optional (`--tor` flag)
- **Notifications**: ✅ Real-time join/leave/connection

### Security Status
- **Overall Score**: 🟢 7.7/10
- **Suitable For**: Trusted networks, development, testing
- **Not For**: Production, high-security, public internet (without Tor)

### Command Examples
```bash
# Normal usage (localhost only)
python3 -m src.main

# With Tor (anonymous)
python3 -m src.main --tor

# Run tests
python3 -m unittest discover -s tests -v

# Help
python3 -m src.main --help
```

## 📧 Support

- **Issues**: Open GitHub issue
- **Security**: See SECURITY_AUDIT.md for contact
- **Contributing**: See README.md Contributing section

---

**Version**: 2.0.0  
**Date**: November 26, 2025  
**Status**: All documentation current and synchronized
