# Internet Connectivity Guide

This guide explains how to use TermTalk over the internet, beyond localhost and LAN.

## Quick Answer

**Yes, TermTalk works over the internet!** The connections use standard TCP sockets with end-to-end encryption, so they work across any network.

## How It Works

### Architecture
- **Registry**: File-based (`~/.termtalk_rooms.json`) - **local machine only**
- **Connections**: TCP sockets with E2EE - **work over any network** (localhost/LAN/internet)

### Connection Flow
1. Host creates a room and binds to IP address
2. Host shares Room ID + IP:port with peer
3. Peer looks up Room ID in local registry
4. If not found → **prompts for host IP:port** (NEW in v2.0.1)
5. Peer connects directly using host IP:port
6. Encrypted channel established via X25519 ECDH + ChaCha20-Poly1305

## Internet Setup Guide

### Host Setup (Making Your Room Accessible)

**1. Configure Router Port Forwarding**
```
Router Settings → Port Forwarding → Add Rule:
  External Port: 12345
  Internal IP: <your local IP, e.g., 192.168.1.100>
  Internal Port: 12345
  Protocol: TCP
```

**2. Start TermTalk Host**
```bash
python3 -m src.cli.main
# Choose: 1 (Host a room)
# Enter IP: 0.0.0.0  (binds all interfaces)
# Enter port: 12345
# Room ID generated: a3f5d7b9e2c4f6a8
```

**3. Find Your Public IP**
```bash
curl ifconfig.me
# Example output: 203.0.113.45
```

**4. Share Connection Info**
Send to your peer:
- **Room ID**: `a3f5d7b9e2c4f6a8`
- **Public IP**: `203.0.113.45`
- **Port**: `12345`

### Peer Setup (Connecting from Internet)

**1. Start TermTalk Peer**
```bash
python3 -m src.cli.main
# Choose: 2 (Join a room)
# Enter Room ID: a3f5d7b9e2c4f6a8
```

**2. Direct Connection Prompt**
```
[CLI] Room 'a3f5d7b9e2c4f6a8' not found in local registry.
[INFO] For LAN/Internet connections, enter host details directly:
Enter host IP address: 203.0.113.45
Enter host port: 12345
```

**3. Connection Established**
```
✅ Successfully connected to 203.0.113.45:12345
🔒 Secure encrypted channel established
```

## Network Modes Comparison

| Mode | Host Binding | Use Case | Registry Works? | Port Forwarding? |
|------|--------------|----------|-----------------|------------------|
| **Localhost** | `127.0.0.1` | Same-machine testing | ✅ Yes | ❌ Not needed |
| **LAN** | Local IP (192.168.x.x) | Private network | ✅ Yes (same subnet) | ❌ Not needed |
| **Internet** | `0.0.0.0` | Remote connections | ❌ No (use direct IP) | ✅ Required |

## Security Considerations

### ⚠️ Internet Exposure Risks

**What's Exposed:**
- Your public IP address (visible to peer)
- Connection timing and message sizes (metadata)
- Open port on your router

**What's Protected:**
- ✅ Message content (ChaCha20-Poly1305 AEAD encryption)
- ✅ Key exchange (X25519 ECDH with forward secrecy)
- ✅ Authentication tags (prevents tampering)

### 🛡️ Security Recommendations

**1. Use Tor for IP Privacy**
```bash
# Both host and peer should use Tor
python3 -m src.cli.main --tor
```
Hides your public IP from the peer.

**2. Use VPN**
- Route traffic through VPN to hide home IP
- Peer sees VPN exit node IP instead

**3. Short Room TTLs**
```bash
# Expire room after 5 minutes (default)
Room duration in seconds: 300
```

**4. Firewall Rules**
```bash
# Only allow connections on specific port
sudo ufw allow 12345/tcp
sudo ufw enable
```

**5. Close Port After Session**
```bash
# Remove port forwarding rule from router when done
# Or close port in firewall:
sudo ufw delete allow 12345/tcp
```

### ⚠️ Known Limitations

**NO MITM Protection:**
- Key exchange lacks fingerprint verification
- Cannot detect man-in-the-middle attacks
- **Trust-on-first-use model** (like SSH on first connection)

**Metadata Leakage:**
- Connection timing visible to network observers
- Message sizes not padded (traffic analysis possible)
- Without Tor: IP addresses exposed

**No Authentication:**
- Anyone with Room ID + IP:port can join
- No room passwords (future feature)

## Advanced: Tor Hidden Service

For maximum privacy, host as a Tor hidden service (.onion address):

**Benefits:**
- No port forwarding needed
- No public IP exposure
- NAT traversal built-in
- End-to-end encryption + onion routing

**Setup (Future Feature):**
```bash
# Configure Tor hidden service
# Edit /etc/tor/torrc:
HiddenServiceDir /var/lib/tor/termtalk/
HiddenServicePort 12345 127.0.0.1:12345

# Start host
python3 -m src.cli.main --tor
# Share .onion address with peer
```

*Note: Full hidden service support requires additional implementation.*

## Troubleshooting

### Connection Refused
**Symptom:** `[CLI] Failed to connect to host: [Errno 111] Connection refused`

**Solutions:**
1. Check port forwarding is configured on router
2. Verify firewall allows connections: `sudo ufw status`
3. Confirm host is running: `netstat -ln | grep 12345`
4. Test with telnet: `telnet <public_ip> 12345`

### Timeout
**Symptom:** `[CLI] Failed to connect to host: [Errno 110] Connection timed out`

**Solutions:**
1. Check host's public IP is correct: `curl ifconfig.me`
2. Verify router's external IP matches
3. Test if port is open: `nmap -p 12345 <public_ip>`
4. Check ISP doesn't block incoming connections (CGNAT)

### Behind CGNAT
Some ISPs use Carrier-Grade NAT, preventing incoming connections.

**Workaround:**
- Use VPN with port forwarding (e.g., Mullvad, ProtonVPN)
- Use reverse proxy service (e.g., ngrok, Cloudflare Tunnel)
- Request public IP from ISP (may cost extra)

### NAT Traversal
**Problem:** Both peers behind NAT, neither can forward ports.

**Solutions:**
1. Use relay server (implement TURN-like protocol)
2. Use Tor (both peers) - works through NAT
3. Use VPN with one endpoint having public IP
4. Implement hole punching (STUN-like, future feature)

## Performance

### Latency
- **Localhost**: <1ms
- **LAN**: 1-5ms
- **Internet (direct)**: 10-100ms (depends on distance)
- **Internet (via Tor)**: 500-2000ms (multiple hops)

### Bandwidth
- **Overhead**: ~40 bytes per message (nonce + auth tag)
- **Throughput**: Limited by network, not crypto (ChaCha20 is fast)

## Example Scenarios

### Scenario 1: Friend on Different Network
```
You: Home (public IP: 203.0.113.45)
Friend: Coffee shop WiFi

Setup:
1. Forward port 12345 on your router
2. python3 -m src.cli.main → Host (IP: 0.0.0.0, port: 12345)
3. Share: Room ID + 203.0.113.45:12345
4. Friend: python3 -m src.cli.main → Join → Enter your IP:port
```

### Scenario 2: Both Use Tor
```
You: python3 -m src.cli.main --tor → Host
Friend: python3 -m src.cli.main --tor → Join

Benefits:
- Neither IP exposed
- Works through NAT/firewalls
- Onion routing privacy

Tradeoff:
- Higher latency (~1-2 seconds)
```

### Scenario 3: VPN + Internet
```
You: Connect to VPN → Host on VPN IP
Friend: Direct internet connection

Benefits:
- Your home IP hidden (VPN IP shown)
- Port forwarding through VPN
- Friend doesn't use Tor (faster)
```

## Future Improvements

Potential enhancements for internet connectivity:

1. **Distributed Registry** (Redis/HTTP-based)
   - Cross-machine room discovery
   - No need to manually share IP:port

2. **NAT Traversal** (STUN/TURN)
   - Connect without port forwarding
   - Automatic hole punching

3. **Hidden Service Support**
   - Native .onion hosting
   - Built-in NAT traversal

4. **Relay Servers**
   - Public relay nodes for NAT traversal
   - Privacy-preserving forwarding

5. **DHT Discovery** (BitTorrent-like)
   - Decentralized room discovery
   - No central registry

## Security Checklist for Internet Use

Before hosting on the internet:

- [ ] Understand MITM risk (no key fingerprint verification)
- [ ] Use `--tor` flag or VPN to hide public IP
- [ ] Configure firewall to only allow specific port
- [ ] Use short TTL (5 minutes default)
- [ ] Close port forwarding after session
- [ ] Don't reuse Room IDs
- [ ] Verify connection info before sharing
- [ ] Consider using VPN endpoint instead of home IP

## Summary

**TL;DR:**
1. TermTalk **DOES work over the internet** ✅
2. Registry is local-only, but connections work anywhere
3. Use direct IP:port input for internet connections (v2.0.1+)
4. Requires port forwarding on host side
5. Use `--tor` flag for IP privacy
6. Be aware of MITM and metadata risks

For maximum security over internet:
```bash
# Both sides:
python3 -m src.cli.main --tor
```

For questions, see:
- [README.md](../README.md) - General usage
- [docs/PRIVACY.md](PRIVACY.md) - Privacy protections
- [docs/TOR_GUIDE.md](TOR_GUIDE.md) - Tor integration
- [docs/threat_model.md](threat_model.md) - Security analysis
