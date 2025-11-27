import random
import string
import socket
import time
from typing import Optional


def random_token(length: int = 6) -> str:
    """makes random token for ids"""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def get_local_ip() -> str:
    """tries to get local ip by connecting to public host
    
    doesnt actually send data but lets os
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
