# Threat Model — TermTalk (reference)

## Summary
TermTalk is a small, peer-to-peer terminal chat prototype. This threat model documents the expected assets, assumptions, and primary threats for the reference implementation and highlights mitigations and residual risks.

## Assets
- Confidentiality of chat messages (primary asset).
- Session keys held in memory during a chat.
- Availability of the host's listening socket while a room is active.

## Assumptions
- Users operate on devices they control.
- Machines are reasonably up-to-date; the OS and Python runtime are not fully compromised.
- The reference implementation runs as a demo — no central discovery service is provided by default.

## Threats
- Network eavesdropping: passive adversary captures network traffic.
- Active MitM (man-in-the-middle): adversary intercepts and modifies handshake messages.
- Host compromise: attacker with access to host machine memory can extract keys.
- Room discovery leakage: sharing of host IP/port or Room ID with untrusted parties leaks metadata.

## Mitigations (reference implementation)
- Message integrity: messages carry an HMAC (HMAC-SHA256) verified before decryption.
- Ephemeral rooms: rooms expire after a TTL and the reference code clears in-memory session data when closed.
- Minimal logging: the reference implementation prints minimal runtime messages and does not persist chat logs.

## Residual risks and recommendations
- Cryptography in the reference implementation is intentionally minimal for clarity and tests. Replace with authenticated encryption (AEAD) and a secure key agreement (e.g., X25519 + HKDF) for production.
- Room discovery is local-only in the reference code; a public rendezvous server should be designed carefully to avoid leaking metadata. Use short-lived registration tokens and authentication if you add a registry.
- Hosts should run behind appropriate network protections (firewalls, NAT) and avoid hosting on public IPs without additional protections.

