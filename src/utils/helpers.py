import random
import string
import socket
import time
import random
import string
import socket
import time
from typing import Optional


def random_token(length: int = 6) -> str:
    """Return a small random token useful for IDs in tests/demos."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get_local_ip() -> str:
    """Try to determine the local IP address by connecting to a public host.

    This doesn't actually send data to the remote host, but lets the OS
    pick a suitable outbound interface. Falls back to localhost on failure.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def countdown_timer(seconds: int, socket_handler: Optional[object] = None) -> None:
    for _ in range(seconds, 0, -1):
        time.sleep(1)
    print("[INFO] Room TTL expired. Shutting down...")
    if socket_handler is not None and getattr(socket_handler, "server_socket", None):
        try:
            socket_handler.server_socket.close()
        except Exception:
            pass
