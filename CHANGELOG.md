# changelog

## version 2.1.0 - current

### what changed
- added optional room password protection
- passwords are hashed with SHA256 before storing
- host can set password when creating room
- joiners need to enter password if room is protected
- updated readme with learning project disclaimer

## version 2.0.1 - dec 18 2025

### what changed
- added direct ip connection mode so you can connect over internet
- if room id not found it now asks for host ip and port
- updated readme with better network instructions

## version 2.0.0 - nov 26 2025

### major changes
- switched to proper encryption (ChaCha20-Poly1305 AEAD)
- added key exchange using X25519 ECDH
- changed default to localhost only instead of 0.0.0.0
- added tor support with --tor flag
- made room ids longer (16 chars instead of 8)
- added connection limits and rate limiting
- added privacy protection so no mac addresses or hostnames leak

### security stuff
- 256 bit encryption keys
- forward secrecy with ephemeral keys
- connection limits: 5 per ip, 50 total
- rate limiting: 10 connections per minute per ip
- socket timeouts to prevent hanging
- input validation on keys and messages

### privacy stuff
- room ids and peer ids are random, not based on hardware
- no mac addresses exposed
- no hostnames or usernames leaked
- error messages dont show file paths
- registry file has restricted permissions (owner only)

### tor integration
- optional tor routing with --tor flag
- works with tor proxy on port 9050
- hides your ip from peers
- instructions in TOR_GUIDE.md

### other improvements
- colored terminal output
- notifications when people join/leave
- better error handling
- comprehensive test suite (30 tests)

## version 1.0.0 - initial release

### what it had
- basic p2p terminal chat
- hmac message authentication (no encryption!)
- simple key derivation
- ephemeral rooms with ttl
- file based registry
- basic cli

### problems (fixed in 2.0)
- no encryption only hmac
- insecure key exchange
- bound to 0.0.0.0 by default
- no connection limits
- no rate limiting
- weak room ids
- world readable registry file

## notes

- version 1.0 was not secure dont use it
- version 2.0 is much better but still a learning project
- use tor if you want ip privacy
- this is not professionally audited
