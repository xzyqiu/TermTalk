# Tor Integration Guide

## Overview

TermTalk supports routing connections through the Tor network for enhanced anonymity and privacy. This feature uses SOCKS5 proxy to tunnel all socket connections through a local Tor daemon.

## Prerequisites

### Install Tor

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install tor
sudo systemctl start tor
sudo systemctl enable tor  # Start on boot
```

**macOS:**
```bash
brew install tor
brew services start tor
```

**Check Tor is running:**
```bash
# Check if Tor SOCKS5 proxy is listening
netstat -an | grep 9050
# or
ss -tuln | grep 9050

# Should show: 127.0.0.1:9050 in LISTEN state
```

## Usage

### Basic Tor Mode
```bash
python3 -m src.main --tor
```

This will:
- Route all connections through Tor (127.0.0.1:9050)
- Add ~1-2 seconds latency per connection
- Hide your real IP address from peers
- Display 🧅 Tor Mode indicator

### Custom Tor Port
If your Tor daemon uses a different port:
```bash
python3 -m src.main --tor --tor-port 9150
```

### Example Session

**Terminal 1 (Host):**
```bash
$ python3 -m src.main --tor
[TOR] Tor mode enabled - connections will route through SOCKS5 proxy
[TOR] Using Tor proxy at 127.0.0.1:9050
[TOR] Make sure Tor is running (e.g., systemctl start tor)
Welcome to TermTalk
🧅 Tor Mode Active
1. Host a room
2. Join a room
Select an option: 1
[SECURITY] Default binding is localhost (127.0.0.1) - only accessible from this machine
[WARNING] Use 0.0.0.0 to bind all interfaces (exposes to network/internet)
Enter your IP to host (default 127.0.0.1): 
Enter port to listen on (default 12345): 
Room duration in seconds (default 300): 
[CLI] Room created! Room ID: a1b2c3d4e5f6g7h8
[CLI] Waiting for peers... (expires in 300s)
Peers should join by entering the Room ID (not your IP).
```

**Terminal 2 (Join):**
```bash
$ python3 -m src.main --tor
[TOR] Tor mode enabled - connections will route through SOCKS5 proxy
Welcome to TermTalk
🧅 Tor Mode Active
1. Host a room
2. Join a room
Select an option: 2
Enter Room ID to join: a1b2c3d4e5f6g7h8
```

## How It Works

1. **PySocks Library**: Uses `PySocks` to wrap Python's socket library with SOCKS5 support
2. **Transparent Proxying**: All socket connections automatically route through Tor
3. **DNS Resolution**: DNS lookups also happen through Tor (prevents DNS leaks)
4. **Encryption**: Tor provides transport encryption on top of TermTalk's E2E encryption

## Security Benefits

### What Tor Protects:
- ✅ **IP Address**: Your real IP is hidden from peers
- ✅ **Network Location**: Geographic location obscured
- ✅ **ISP Surveillance**: ISP only sees Tor traffic, not destination
- ✅ **Traffic Analysis**: Makes it harder to correlate traffic patterns
- ✅ **Censorship Bypass**: Can access services blocked by firewall

### What Tor Doesn't Protect:
- ❌ **Message Content**: Already protected by TermTalk's E2E encryption
- ❌ **Traffic Timing**: Sophisticated attackers can correlate timing
- ❌ **Application Fingerprinting**: TermTalk's protocol can be identified
- ❌ **Exit Node Snooping**: Exit node can see outgoing connections (but not content)

## Performance Impact

| Metric | Normal Mode | Tor Mode |
|--------|-------------|----------|
| **Connection Setup** | ~10-50ms | ~1-2 seconds |
| **Message Latency** | ~5-20ms | ~100-500ms |
| **Throughput** | Full bandwidth | Limited by Tor network |
| **Reliability** | High | Moderate (Tor circuits can fail) |

## Troubleshooting

### "Tor is not running" Error
```bash
# Check Tor status
sudo systemctl status tor

# Start Tor if not running
sudo systemctl start tor
```

### "Connection refused" to 127.0.0.1:9050
```bash
# Verify Tor is listening
netstat -tuln | grep 9050

# Check Tor configuration
cat /etc/tor/torrc | grep SocksPort
# Should have: SocksPort 9050
```

### Slow Connections
- This is normal - Tor routes through 3+ relay nodes
- Each connection takes 1-2 seconds to establish circuit
- Consider if anonymity benefit is worth the latency

### Connection Failures
```bash
# Tor circuits can fail - retry or restart Tor
sudo systemctl restart tor

# Check Tor logs
sudo journalctl -u tor -f
```

### Testing Tor Connection
```python
# In Python console
from src.transport.tor_proxy import test_tor_connection
test_tor_connection()  # Should return True if Tor is accessible
```

## Best Practices

### Do:
1. **Use Tor on both ends** for maximum anonymity (host and client)
2. **Share Room IDs securely** (encrypted channels like Signal)
3. **Use unique Room IDs** for each session
4. **Monitor Tor status** before starting sessions
5. **Be patient** with connection delays

### Don't:
1. **Don't mix Tor and non-Tor** peers in same session (degrades anonymity)
2. **Don't share real identity** information in messages
3. **Don't use with untrusted Room IDs** (could be honeypots)
4. **Don't assume complete anonymity** (sophisticated adversaries exist)
5. **Don't use for time-sensitive** communications (latency varies)

## Advanced Configuration

### Tor Browser's SOCKS Port
If using Tor Browser (port 9150):
```bash
python3 -m src.main --tor --tor-port 9150
```

### Tor Configuration File
Edit `/etc/tor/torrc` for custom settings:
```
# Custom SOCKS port
SocksPort 9051

# Increase circuit timeout
CircuitBuildTimeout 60

# Use specific exit nodes (optional)
ExitNodes {US},{GB},{CA}
```

Then restart Tor:
```bash
sudo systemctl restart tor
```

## .onion Service Support (Future)

Currently, TermTalk hosts bind to regular IP addresses. Future enhancements could include:
- **Hidden Services**: Host on .onion address
- **Bridge Support**: Connect through Tor bridges
- **Pluggable Transports**: Obfuscate Tor traffic

## Security Considerations

### Threat Model
- **Protects against**: ISP surveillance, network observers, geographic tracking
- **Vulnerable to**: Global passive adversaries, traffic correlation, timing attacks
- **Recommendation**: Use for privacy, not for evading determined nation-state attackers

### Operational Security
1. **Don't log real IPs** anywhere when using Tor
2. **Clear registry file** after sensitive sessions
3. **Use ephemeral Room IDs** (don't reuse)
4. **Consider VPN + Tor** for additional layer (controversial, research first)

## Resources

- **Tor Project**: https://www.torproject.org/
- **Tor Browser**: https://www.torproject.org/download/
- **PySocks Documentation**: https://github.com/Anorov/PySocks
- **Tor Hidden Services**: https://community.torproject.org/onion-services/

## Testing

Run security tests with Tor enabled:
```bash
# Note: Tests don't use Tor by default
# Manual testing recommended for Tor functionality
python3 -m src.main --tor
```

---

**Note**: Tor provides network-level anonymity, not application-level security. TermTalk's E2E encryption protects message content; Tor protects connection metadata.
