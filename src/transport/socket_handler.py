import socket
import threading
import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
from src.crypto.handshake import Handshake
from src.crypto.box import SecureBox


class EncryptedHostSocket:
    # this is the server socket that accepts connections
    def __init__(self, host: str, port: int, room=None, max_connections: int = 50, max_per_ip: int = 5):
        self.host = host
        self.port = port
        self.room = room  # room object for password checking
        # setup socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(30)  # timeout for accepting
        self.connections: Dict[str, Tuple[socket.socket, SecureBox]] = {}
        self.connections_per_ip: Dict[str, int] = defaultdict(int)
        self.connection_timestamps: Dict[str, list] = defaultdict(list)
        self.banned_ips: set = set()  # ips banned for wrong passwords
        self.max_connections = max_connections
        self.max_per_ip = max_per_ip
        self.running = True

    def start(self) -> None:
        # bind and start listening
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        # start thread to accept connections
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self) -> None:
        # keep accepting connections
        while self.running:
            try:
                conn, addr = self.sock.accept()
                # check if ip is banned
                if addr[0] in self.banned_ips:
                    print(f"[SECURITY] Banned IP attempted connection: {addr[0]}")
                    conn.close()
                    continue
                # check if too many connections
                if len(self.connections) >= self.max_connections:
                    print(f"[SECURITY] Max connections reached, rejecting {addr[0]}")
                    conn.close()
                    continue
                # check if ip has too many connections
                if self.connections_per_ip[addr[0]] >= self.max_per_ip:
                    print(f"[SECURITY] Max connections per IP reached for {addr[0]}")
                    conn.close()
                    continue
                
                # rate limiting - max 10 per minute per ip
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
            conn.sendall((handshake.get_public_key_str() + "\n").encode())
            peer_pub_key = conn.recv(1024).decode().strip()
            
            if not peer_pub_key or len(peer_pub_key) > 512:
                print(f"[SECURITY] Invalid public key length from {peer_ip}")
                return
            
            #Key exchange
            try:
                shared_key = handshake.generate_shared_box(peer_pub_key)
                secure_box = SecureBox(shared_key)
            except Exception as e:
                from src.utils.privacy import sanitize_error_message
                print(f"[SECURITY] Handshake failed with {peer_ip}: {sanitize_error_message(e)}")
                return
            
            # check password if room has one
            if self.room and self.room.password_hash is not None:
                attempts = 0
                max_attempts = 3
                while attempts < max_attempts:
                    conn.sendall(secure_box.encrypt("PASSWORD_REQUIRED").encode())
                    password_data = conn.recv(4096)
                    if not password_data:
                        print(f"[SECURITY] No password provided from {peer_ip}")
                        return
                    password = secure_box.decrypt(password_data.decode())
                    if self.room.verify_password(password):
                        conn.sendall(secure_box.encrypt("PASSWORD_OK").encode())
                        break
                    else:
                        attempts += 1
                        if attempts >= max_attempts:
                            conn.sendall(secure_box.encrypt("PASSWORD_BANNED").encode())
                            self.banned_ips.add(peer_ip)
                            print(f"[SECURITY] IP banned for failed password attempts: {peer_ip}")
                            return
                        else:
                            conn.sendall(secure_box.encrypt(f"PASSWORD_INCORRECT:{max_attempts - attempts}").encode())
                            print(f"[SECURITY] Incorrect password from {peer_ip} (attempt {attempts}/{max_attempts})")
            
            self.connections[peer_id] = (conn, secure_box)
            
            from termcolor import colored
            # peer joined notification
            print(colored(f"\n[JOIN] Peer {peer_ip} joined the room! ({len(self.connections)} peer(s) connected)", "green"))

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
                except Exception as e:
                    print(f"[{peer_id}] Error: {type(e).__name__}")
                    break
        finally:
            try:
                conn.close()
            except Exception:
                pass
            was_connected = peer_id in self.connections
            self.connections.pop(peer_id, None)
            self.connections_per_ip[peer_ip] -= 1
            if self.connections_per_ip[peer_ip] <= 0:
                del self.connections_per_ip[peer_ip]
            
            if was_connected:
                from termcolor import colored
                # peer left notification
                print(colored(f"\n[LEAVE] Peer {peer_ip} left the room. ({len(self.connections)} peer(s) remaining)", "red"))

    def send_to_all(self, message: str) -> None:
        for peer_id, (conn, secure_box) in list(self.connections.items()):
            try:
                conn.sendall(secure_box.encrypt(message).encode())
            except Exception:
                pass

    def stop(self) -> None:
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass


class EncryptedPeerSocket:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(30)  # 30-second timeout for operations
        self.secure_box: Optional[SecureBox] = None

    def connect(self, password: Optional[str] = None) -> None:
        self.sock.connect((self.host, self.port))
        handshake = Handshake()
        peer_key = self.sock.recv(1024).decode().strip()
        
        if not peer_key or len(peer_key) > 512:
            raise ValueError("Invalid peer key received")
        
        self.sock.sendall((handshake.get_public_key_str() + "\n").encode())
        shared_key = handshake.generate_shared_box(peer_key)
        self.secure_box = SecureBox(shared_key)
        
        # check if password is needed
        from termcolor import colored
        while True:
            first_msg = self.sock.recv(4096)
            if not first_msg:
                break
            decrypted = self.secure_box.decrypt(first_msg.decode())
            if decrypted == "PASSWORD_REQUIRED":
                if not password:
                    password = input(colored("Enter room password: ", "cyan")).strip()
                self.sock.sendall(self.secure_box.encrypt(password).encode())
            elif decrypted.startswith("PASSWORD_INCORRECT:"):
                attempts_left = decrypted.split(":")[1]
                print(colored(f"[CLI] Incorrect password. {attempts_left} attempts remaining.", "red"))
                password = input(colored("Enter room password: ", "cyan")).strip()
                self.sock.sendall(self.secure_box.encrypt(password).encode())
            elif decrypted == "PASSWORD_BANNED":
                print(colored("[CLI] Too many incorrect attempts. You have been banned from this room.", "red"))
                self.sock.close()
                raise Exception("Banned from room")
            elif decrypted == "PASSWORD_OK":
                break
            else:
                break
        
        from termcolor import colored
        # connection successful
        print(colored(f"\n[SUCCESS] Successfully connected to {self.host}:{self.port}", "green"))
        print(colored("[ENCRYPTED] Secure encrypted channel established\n", "cyan"))
        
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
