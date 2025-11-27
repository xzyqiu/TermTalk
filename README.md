# TermTalk

a simple terminal chat app for peer to peer messaging. made as a learning project to understand encryption and networking stuff.

## what it does
- encrypted messaging using ChaCha20-Poly1305 and X25519 key exchange
- connection limits to prevent spam (5 per IP, 50 total)
- privacy protection - no MAC addresses or hostnames exposed
- tor support for anonymous connections
- rooms expire after 5 minutes
- works on localhost, LAN, or internet

## how to use

### setup
```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### host a room
```sh
python3 -m src.main
# pick option 1
# default is localhost (127.0.0.1) - only works on your computer
# for LAN use your local ip like 192.168.1.100
# for internet use 0.0.0.0 and forward the port on your router
```

example:
```
[CLI] Room created! Room ID: d0933719af4a4c89
[CLI] Waiting for peers... (expires in 300s)
```

### join a room
```sh
python3 -m src.main
# pick option 2
# enter the room id
# if not found locally enter host ip and port manually
```

### using tor
if you want to hide your ip address:
```sh
# make sure tor is running first
sudo apt install tor
sudo systemctl start tor

# then run with tor flag
python3 -m src.main --tor
```

tor makes connections slower but more private

## network stuff

**localhost** - only works on same computer
- host ip: 127.0.0.1
- good for testing

**LAN** - works on local network
- host ip: your local ip (like 192.168.1.100)
- works with other computers on same wifi

**internet** - works anywhere
- host ip: 0.0.0.0
- forward port on router
- share your public ip with peers
- WARNING: exposes your ip unless using tor

## how it works

the host creates a room and gets a random room id. other people can join by entering that room id. if the room isnt in the local registry file they can enter the hosts ip and port directly.

all messages are encrypted with ChaCha20-Poly1305. the encryption keys are exchanged using X25519 ECDH so nobody can read your messages even if they intercept them.

rooms expire after 5 minutes by default to keep things temporary.

## security notes

- messages are encrypted end to end
- no MITM protection so first connection is trust based (like ssh)
- your ip is visible to peers unless using tor
- this is a learning project not production ready
- rate limiting prevents spam/dos attacks

## testing
```sh
source venv/bin/activate
python3 -m unittest discover tests
```

should see all tests pass

## requirements
see requirements.txt for dependencies:
- cryptography (for encryption)
- PySocks (for tor)
- termcolor (for colored output)

## project structure
```
src/
  cli/          - command line interface
  crypto/       - encryption stuff
  room/         - room management
  transport/    - networking and sockets
  utils/        - helper functions
tests/          - unit tests
docs/           - documentation
```

## tips

- keep room ttl short (default 5 min is good)
- use tor if you dont want to expose your ip
- for internet connections you need to forward ports on your router
- the registry file is at ~/.termtalk_rooms.json

## known issues

- no key fingerprint verification so cant detect mitm
- registry only works locally not across internet
- no room passwords yet
- not professionally audited

## changelog

see CHANGELOG.md for version history

## license

see LICENSE file

