import threading
import time
import hashlib
from typing import Any, Dict, Optional
from src.room.registry import RoomRegistry
from src.utils.privacy import generate_anonymous_room_id, generate_anonymous_peer_id


class Room:
    # represents a chat room
    def __init__(self, host_ip: str, host_port: int, duration: int, password: Optional[str] = None):
        # make random room id for privacy
        self.room_id = generate_anonymous_room_id()
        self.host_ip = host_ip
        self.host_port = host_port
        self.duration = duration
        self.start_time = time.time()
        self.active = True
        self.peers: Dict[str, dict] = {}
        self.host_socket: Optional[Any] = None  # socket for cleanup
        # hash password if provided
        self.password_hash = self._hash_password(password) if password else None
    
    def _hash_password(self, password: str) -> str:
        # hash password with sha256
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        # check if password matches
        if self.password_hash is None:
            return True  # no password set
        return self._hash_password(password) == self.password_hash

    def add_peer(self, peer_info: Optional[dict] = None) -> str:
        # add a peer and give them random id
        peer_id = generate_anonymous_peer_id()
        self.peers[peer_id] = peer_info or {}
        return peer_id

    def remove_peer(self, peer_id: str) -> None:
        # remove peer from room
        self.peers.pop(peer_id, None)

    def check_expiry(self) -> bool:
        # check if room expired
        if time.time() - self.start_time >= self.duration:
            self.active = False
        return self.active


class RoomManager:
    # manages all the rooms
    def __init__(self, registry: Optional[RoomRegistry] = None):
        self.rooms: Dict[str, Room] = {}
        self.lock = threading.Lock()
        self.registry = registry or RoomRegistry()

    def create_room(self, host_ip: str, host_port: int, duration: int, password: Optional[str] = None) -> Room:
        # make new room
        room = Room(host_ip, host_port, duration, password)
        with self.lock:
            self.rooms[room.room_id] = room
        # register it so others can find it
        expires_at = room.start_time + room.duration
        self.registry.register_room(room.room_id, host_ip, host_port, expires_at)
        # start timer thread
        threading.Thread(target=self._room_timer, args=(room,), daemon=True).start()
        return room

    def get_room(self, room_id: str) -> Optional[Room]:
        # check in memory first
        with self.lock:
            room = self.rooms.get(room_id)
            if room is not None:
                return room
        # check registry file
        room_info = self.registry.get_room(room_id)
        if room_info is None:
            return None
        # create room from registry info
        room = Room(
            host_ip=room_info["host_ip"],
            host_port=room_info["host_port"],
            duration=0 # dont know duration from registry
        )
        room.room_id = room_id
        return room

    def remove_room(self, room_id: str) -> None:
        with self.lock:
            self.rooms.pop(room_id, None)
        self.registry.unregister_room(room_id)

    def _room_timer(self, room: Room) -> None:
        while room.active:
            time.sleep(1)
            room.check_expiry()
        print(f"[ROOM] Room {room.room_id} expired")
        host_socket = getattr(room, "host_socket", None)
        if host_socket is not None and hasattr(host_socket, "stop"):
            try:
                host_socket.stop()
            except Exception:
                pass
        self.remove_room(room.room_id)
