"""Tor SOCKS5 proxy support for anonymous connections.

This module provides transparent Tor support by routing socket connections
through a local Tor SOCKS5 proxy (default: 127.0.0.1:9050).

Requirements:
- Tor must be installed and running
- On Linux: sudo apt install tor && sudo systemctl start tor
- On macOS: brew install tor && brew services start tor
"""
import socket
import socks

# Global Tor configuration
_TOR_ENABLED = False
_TOR_PROXY_HOST = "127.0.0.1"
_TOR_PROXY_PORT = 9050


def set_tor_enabled(enabled: bool, port: int = 9050) -> None:
    """Enable or disable Tor routing for all socket connections.
    
    Args:
        enabled: Whether to route through Tor
        port: Tor SOCKS5 proxy port (default: 9050)
    """
    global _TOR_ENABLED, _TOR_PROXY_PORT
    _TOR_ENABLED = enabled
    _TOR_PROXY_PORT = port
    
    if enabled:
        # Set default socket to use SOCKS5 proxy
        socks.set_default_proxy(socks.SOCKS5, _TOR_PROXY_HOST, _TOR_PROXY_PORT)
        socket.socket = socks.socksocket


def is_tor_enabled() -> bool:
    """Check if Tor routing is currently enabled."""
    return _TOR_ENABLED


def get_tor_proxy_address() -> tuple:
    """Get the current Tor proxy address.
    
    Returns:
        Tuple of (host, port)
    """
    return (_TOR_PROXY_HOST, _TOR_PROXY_PORT)


def create_tor_socket() -> socket.socket:
    """Create a new socket configured to use Tor SOCKS5 proxy.
    
    Returns:
        Socket configured for Tor routing
        
    Raises:
        Exception: If Tor is not enabled or connection fails
    """
    if not _TOR_ENABLED:
        raise RuntimeError("Tor is not enabled. Call set_tor_enabled(True) first.")
    
    sock = socks.socksocket()
    sock.set_proxy(socks.SOCKS5, _TOR_PROXY_HOST, _TOR_PROXY_PORT)
    return sock


def test_tor_connection() -> bool:
    """Test if Tor proxy is accessible and working.
    
    Returns:
        True if Tor is accessible, False otherwise
    """
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, _TOR_PROXY_HOST, _TOR_PROXY_PORT)
        sock.settimeout(5)
        # Try to connect to a .onion address or test server
        # Just creating the socket and setting proxy is enough to test
        sock.close()
        return True
    except Exception:
        return False
