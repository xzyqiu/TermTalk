import socket
import threading
from typing import Dict, Optional, Tuple
from src.crypto.handshake import Handshake
from src.crypto.box import SecureBox


class EncryptedHostSocket:
    """Host socket that performs a simple handshake and manages encrypted peers.

    This implementation is intentionally minimal and intended for demo use
    (test-suite uses higher-level RoomManager). It accepts connections and
    keeps a mapping of `peer_id -> (conn, secure_box)` for sending messages.
    """

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections: Dict[str, Tuple[socket.socket, SecureBox]] = {}
        self.running = True

    def start(self) -> None:
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self) -> None:
        while self.running:
            try:
                conn, addr = self.sock.accept()
            except OSError:
                break
            threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()

    def _handle_client(self, conn: socket.socket, addr) -> None:
        peer_id = str(addr[1])
        handshake = Handshake()
        try:
            conn.sendall((handshake.get_public_key_str() + "\n").encode())
            peer_pub_key = conn.recv(1024).decode().strip()
            secure_box = SecureBox(handshake.generate_shared_box(peer_pub_key))
            self.connections[peer_id] = (conn, secure_box)

            while self.running:
                data = conn.recv(4096)
                if not data:
                    break
                try:
                    decrypted = secure_box.decrypt(data.decode())
                    print(f"[{peer_id}] {decrypted}")
                except Exception:
                    print(f"[{peer_id}] Received corrupted message")
        finally:
            try:
                conn.close()
            except Exception:
                pass
            self.connections.pop(peer_id, None)

    def send_to_all(self, message: str) -> None:
        # Iterate over a snapshot to avoid runtime-dict-changes
        for peer_id, (conn, secure_box) in list(self.connections.items()):
            try:
                conn.sendall(secure_box.encrypt(message).encode())
            except Exception:
                # Ignore broken peers; cleanup happens in _handle_client
                pass

    def stop(self) -> None:
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass


class EncryptedPeerSocket:
    """Client peer socket that connects to an EncryptedHostSocket."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secure_box: Optional[SecureBox] = None

    def connect(self) -> None:
        self.sock.connect((self.host, self.port))
        handshake = Handshake()
        peer_key = self.sock.recv(1024).decode().strip()
        self.sock.sendall((handshake.get_public_key_str() + "\n").encode())
        self.secure_box = SecureBox(handshake.generate_shared_box(peer_key))
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def _recv_loop(self) -> None:
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            try:
                if self.secure_box is None:
                    continue
                decrypted = self.secure_box.decrypt(data.decode())
                print(f"[PEER] {decrypted}")
            except Exception:
                print("[PEER] Received corrupted message")

    def send(self, message: str) -> None:
        if self.secure_box is None:
            raise RuntimeError("Not connected / secure box not initialized")
        self.sock.sendall(self.secure_box.encrypt(message).encode())

    def close(self) -> None:
        try:
            self.sock.close()
        except Exception:
            pass
