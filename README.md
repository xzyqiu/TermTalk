# TermTalk

TermTalk is a small, terminal-based, peer-to-peer chat prototype focused on short-lived, direct messaging sessions. The reference implementation demonstrates the messaging flow, a simple handshake, and an in-memory room system for tests and demos.

This project is a demonstration / learning implementation, not a production-ready secure messenger. See the Threat Model for limitations and recommended improvements.

## Features (reference)
- End-to-end message integrity using HMAC-SHA256 (demo-only).
- Ephemeral rooms with TTL and in-memory room management.
- Simple CLI: host and join sessions from the terminal.

## Quickstart
1. Create a virtual environment and install dependencies:

```sh
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

2. Host a room (runs the CLI entrypoint):

```sh
python -m src.main
# then choose option 1: Host a room
```

3. Join a room (from the same process or another instance that can resolve the Room ID):

```sh
python -m src.main
# then choose option 2: Join a room, and enter the Room ID shown by the host
```

## Running tests
The project includes a small unit test suite. Run:

```sh
python -m unittest discover -v
```

## Security & Limitations
- The reference crypto (HMAC + deterministic shared string) is NOT suitable for production.
- Room discovery in this implementation is process-local. To support cross-machine discovery, implement a secure rendezvous/registry service and protect registration with authentication.
- Do not rely on this project for strong security guarantees without replacing the handshake and encryption primitives with well-reviewed, modern algorithms.

## Contributing
Contributions are welcome. Please open issues for design discussions or feature requests.

