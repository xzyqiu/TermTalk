# Project Status — TermTalk

Status: Alpha (prototype)

- Tests: small unit-suite included and passing in the repository.
- Current focus: make the reference implementation clean, testable, and easy to extend.
- Known limitations:
  - Room discovery is process-local (no public rendezvous/registry).
  - Cryptography is demonstrative only (replace with AEAD + secure key agreement for production).
- Next planned work:
  1. Add optional rendezvous/registry component for cross-machine discovery.
  2. Replace the demo handshake with X25519 + HKDF and AEAD for encryption.
  3. Add CI (tests + linting + formatting) and a packaging story.

