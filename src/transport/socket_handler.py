import socket
import threading
from src.crypto.handshake import Handshake
from src.crypto.box import SecureBox

class EncryptedHostSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = {}
        self.running = True

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while self.running:
            conn, addr = self.sock.accept()
            threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()

    def _handle_client(self, conn, addr):
        peer_id = str(addr[1])
        handshake = Handshake()
        conn.sendall((handshake.get_public_key_str() + "\n").encode())
        peer_pub_key = conn.recv(1024).decode().strip()
        secure_box = SecureBox(handshake.generate_shared_box(peer_pub_key))
        self.connections[peer_id] = (conn, secure_box)

        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break
                decrypted = secure_box.decrypt(data.decode())
                print(f"[{peer_id}] {decrypted}")
        finally:
            conn.close()
            del self.connections[peer_id]

    def send_to_all(self, message):
        for peer_id, (conn, secure_box) in self.connections.items():
            try:
                conn.sendall(secure_box.encrypt(message).encode())
            except:
                pass

    def stop(self):
        self.running = False
        self.sock.close()


class EncryptedPeerSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.secure_box = None

    def connect(self):
        self.sock.connect((self.host, self.port))
        handshake = Handshake()
        peer_key = self.sock.recv(1024).decode().strip()
        self.sock.sendall((handshake.get_public_key_str() + "\n").encode())
        self.secure_box = SecureBox(handshake.generate_shared_box(peer_key))
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def _recv_loop(self):
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            try:
                decrypted = self.secure_box.decrypt(data.decode())
                print(f"[PEER] {decrypted}")
            except:
                print("[PEER] Received corrupted message")

    def send(self, message):
        self.sock.sendall(self.secure_box.encrypt(message).encode())

    def close(self):
        self.sock.close()
