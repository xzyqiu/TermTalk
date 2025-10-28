import random
import string
import socket
import time

def random_token(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def countdown_timer(seconds, socket_handler=None):
    for i in range(seconds, 0, -1):
        time.sleep(1)
    print("[INFO] Room TTL expired. Shutting down...")
    if socket_handler and socket_handler.server_socket:
        socket_handler.server_socket.close()
