import socket
import socks

# global vars for tor settings
_TOR_ENABLED = False
_TOR_PROXY_HOST = "127.0.0.1"
_TOR_PROXY_PORT = 9050


def set_tor_enabled(enabled: bool, port: int = 9050) -> None:
    # turn tor on or off
    global _TOR_ENABLED, _TOR_PROXY_PORT
    _TOR_ENABLED = enabled
    _TOR_PROXY_PORT = port
    
    if enabled:
        # make all sockets use tor proxy
        socks.set_default_proxy(socks.SOCKS5, _TOR_PROXY_HOST, _TOR_PROXY_PORT)
        socket.socket = socks.socksocket


def is_tor_enabled() -> bool:
    # check if tor is on
    return _TOR_ENABLED


def get_tor_proxy_address() -> tuple:
    # return tor proxy address
    return (_TOR_PROXY_HOST, _TOR_PROXY_PORT)


def create_tor_socket() -> socket.socket:
    # make a socket that uses tor
    if not _TOR_ENABLED:
        raise RuntimeError("Tor is not enabled. Call set_tor_enabled(True) first.")
    
    sock = socks.socksocket()
    sock.set_proxy(socks.SOCKS5, _TOR_PROXY_HOST, _TOR_PROXY_PORT)
    return sock


def test_tor_connection() -> bool:
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, _TOR_PROXY_HOST, _TOR_PROXY_PORT)
        sock.settimeout(5)
        sock.close()
        return True
    except Exception:
        return False
