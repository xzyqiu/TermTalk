# using tor with termtalk

## what is tor

tor routes your connection through multiple servers so nobody can see your real ip address. makes you more anonymous but also slower.

## installing tor

### linux
```bash
sudo apt update
sudo apt install tor
sudo systemctl start tor
```

check its running:
```bash
netstat -an | grep 9050
# should show 127.0.0.1:9050
```

### mac
```bash
brew install tor
brew services start tor
```

## how to use it

just add --tor flag when running:
```bash
python3 -m src.main --tor
```

thats it! all connections will go through tor now.

### custom port
if tor is on different port:
```bash
python3 -m src.main --tor --tor-port 9150
```

## example

host with tor:
```bash
python3 -m src.main --tor
# pick option 1 to host
# your ip will be hidden from peers
```

join with tor:
```bash
python3 -m src.main --tor
# pick option 2 to join
# your ip will be hidden from host
```

## how it works

termtalk uses PySocks to route all socket connections through the tor SOCKS5 proxy running on 127.0.0.1:9050. this means:
- all tcp connections go through tor network
- your real ip is hidden
- connection goes through 3 random tor nodes
- each node only knows the previous and next node

## performance

tor adds latency:
- normal connection: 10-100ms
- with tor: 500-2000ms (half second to 2 seconds)

its noticeably slower but worth it for privacy

## troubleshooting

### tor not running
```
error: [Errno 111] connection refused
```
solution: start tor service
```bash
sudo systemctl start tor
```

### wrong port
```
error: proxy connection failed
```
solution: check tor port (usually 9050)
```bash
netstat -an | grep LISTEN | grep tor
```

### tor not installed
```
ModuleNotFoundError: No module named 'socks'
```
solution: install dependencies
```bash
pip install -r requirements.txt
```

## security notes

### what tor protects
- hides your ip from peers
- hides which peer youre connecting to from your isp
- prevents network monitoring
- makes location tracking harder

### what tor doesnt protect
- messages are still visible to peer (but encrypted)
- room ids are still visible if intercepted
- timing analysis still possible
- exit node can see youre using termtalk (but not content)

### best practices
- use tor on both host and peer for full anonymity
- dont share personal info in messages
- use short room ttls
- dont reuse room ids

## advanced

### checking tor circuit
you can check which nodes your connection uses:
```bash
# connect to tor control port
telnet 127.0.0.1 9051
# authenticate
authenticate ""
# get circuit info
getinfo circuit-status
```

### using tor browser tor
tor browser uses port 9150 by default:
```bash
python3 -m src.main --tor --tor-port 9150
```

## is tor legal

yes tor is legal in most countries. its used by:
- journalists protecting sources
- activists in restrictive countries
- people who value privacy
- researchers
- normal people who dont want to be tracked

some countries try to block tor but its not illegal to use it in most places.

## summary

tor makes termtalk connections anonymous by:
1. routing through multiple random servers
2. hiding your ip from peers
3. encrypting connection multiple times

tradeoffs:
- slower (1-2 second delay)
- requires tor daemon running
- both sides should use tor for full anonymity

worth it if you need privacy!
