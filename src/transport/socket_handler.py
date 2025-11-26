import socket
import threading
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
from src.crypto.handshake import Handshake
from src.crypto.box import SecureBox


class EncryptedHostSocket:
    """Host socket that performs a simple handshake and manages encrypted peers.

    This implementation is intentionally minimal and intended for demo use
    (test-suite uses higher-level RoomManager). It accepts connections and
    keeps a mapping of `peer_id -> (conn, secure_box)` for sending messages.
    
    Security features:
    - Connection limits per IP and globally
    - Socket timeouts to prevent resource exhaustion
    - Rate limiting for new connections
    """

    def __init__(self, host: str, port: int, max_connections: int = 50, max_per_ip: int = 5):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(30)  # Accept timeout
        self.connections: Dict[str, Tuple[socket.socket, SecureBox]] = {}
        self.connections_per_ip: Dict[str, int] = defaultdict(int)
        self.connection_timestamps: Dict[str, list] = defaultdict(list)
        self.max_connections = max_connections
        self.max_per_ip = max_per_ip
        self.running = True

    def start(self) -> None:
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self) -> None:
        while self.running:
            try:
                conn, addr = self.sock.accept()
                
                # Check global connection limit
                if len(self.connections) >= self.max_connections:
                    print(f"[SECURITY] Max connections reached, rejecting {addr[0]}")
                    conn.close()
                    continue
                
                # Check per-IP connection limit
                if self.connections_per_ip[addr[0]] >= self.max_per_ip:
                    print(f"[SECURITY] Max connections per IP reached for {addr[0]}")
                    conn.close()
                    continue
                
                # Rate limiting: max 10 connections per minute per IP
                now = time.time()
                recent_connections = [t for t in self.connection_timestamps[addr[0]] if now - t < 60]
                self.connection_timestamps[addr[0]] = recent_connections
                
                if len(recent_connections) >= 10:
                    print(f"[SECURITY] Rate limit exceeded for {addr[0]}")
                    conn.close()
                    continue
                
                self.connection_timestamps[addr[0]].append(now)
                self.connections_per_ip[addr[0]] += 1
                
                # Set timeout on client connection
                conn.settimeout(60)
                
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()

    def _handle_client(self, conn: socket.socket, addr) -> None:
        peer_id = str(addr[1])
        peer_ip = addr[0]
        handshake = Handshake()
        try:
            # Send our public key
            conn.sendall((handshake.get_public_key_str() + "\n").encode())
            
            # Receive peer public key with size limit
            peer_pub_key = conn.recv(1024).decode().strip()
            
            if not peer_pub_key or len(peer_pub_key) > 512:
                print(f"[SECURITY] Invalid public key length from {peer_ip}")
                return
            
            # Perform key exchange
            try:
                shared_key = handshake.generate_shared_box(peer_pub_key)
                secure_box = SecureBox(shared_key)
            except Exception as e:
                print(f"[SECURITY] Handshake failed with {peer_ip}: {type(e).__name__}")
                return
            
            self.connections[peer_id] = (conn, secure_box)

            while self.running:
                try:
                    data = conn.recv(4096)
                    if not data:
                        break
                    
                    # Validate size before processing
                    if len(data) > 65536:  # 64 KB limit
                        print(f"[SECURITY] Oversized message from {peer_ip}")
                        break
                    
                    decrypted = secure_box.decrypt(data.decode())
                    print(f"[{peer_id}] {decrypted}")
                except socket.timeout:
                    print(f"[{peer_id}] Connection timeout")
                    break
                except ValueError:
                    print(f"[{peer_id}] Message authentication failed")
                    # Don't break - could be network corruption
                except Exception as e:
                    print(f"[{peer_id}] Error: {type(e).__name__}")
                    break
        finally:
            try:
                conn.close()
            except Exception:
                pass
            self.connections.pop(peer_id, None)
            self.connections_per_ip[peer_ip] -= 1
            if self.connections_per_ip[peer_ip] <= 0:
                del self.connections_per_ip[peer_ip]

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
        self.sock.settimeout(30)  # 30-second timeout for operations
        self.secure_box: Optional[SecureBox] = None

    def connect(self) -> None:
        self.sock.connect((self.host, self.port))
        handshake = Handshake()
        peer_key = self.sock.recv(1024).decode().strip()
        
        if not peer_key or len(peer_key) > 512:
            raise ValueError("Invalid peer key received")
        
        self.sock.sendall((handshake.get_public_key_str() + "\n").encode())
        shared_key = handshake.generate_shared_box(peer_key)
        self.secure_box = SecureBox(shared_key)
        threading.Thread(target=self._recv_loop, daemon=True).start()

    def _recv_loop(self) -> None:
        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                
                if len(data) > 65536:  # 64 KB limit
                    print("[PEER] Oversized message received")
                    break
                
                if self.secure_box is None:
                    continue
                
                decrypted = self.secure_box.decrypt(data.decode())
                print(f"[PEER] {decrypted}")
            except socket.timeout:
                print("[PEER] Connection timeout")
                break
            except ValueError:
                print("[PEER] Message authentication failed")
            except Exception as e:
                print(f"[PEER] Error: {type(e).__name__}")
                break

    def send(self, message: str) -> None:
        if self.secure_box is None:
            raise RuntimeError("Not connected / secure box not initialized")
        self.sock.sendall(self.secure_box.encrypt(message).encode())

    def close(self) -> None:
        try:
            self.sock.close()
        except Exception:
            pass
