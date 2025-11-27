import threading
import time
from typing import Any, Dict, Optional
from src.room.registry import RoomRegistry
from src.utils.privacy import generate_anonymous_room_id, generate_anonymous_peer_id


class Room:
    def __init__(self, host_ip: str, host_port: int, duration: int):
        # Privacy-preserving anonymous room ID
        self.room_id = generate_anonymous_room_id()
        self.host_ip = host_ip
        self.host_port = host_port
        self.duration = duration
        self.start_time = time.time()
        self.active = True
        self.peers: Dict[str, dict] = {}
        self.host_socket: Optional[Any] = None  # Optional EncryptedHostSocket for cleanup

    def add_peer(self, peer_info: Optional[dict] = None) -> str:
        # Privacy-preserving anonymous peer ID
        peer_id = generate_anonymous_peer_id()
        self.peers[peer_id] = peer_info or {}
        return peer_id

    def remove_peer(self, peer_id: str) -> None:
        self.peers.pop(peer_id, None)

    def check_expiry(self) -> bool:
        if time.time() - self.start_time >= self.duration:
            self.active = False
        return self.active


class RoomManager:
    def __init__(self, registry: Optional[RoomRegistry] = None):
        self.rooms: Dict[str, Room] = {}
        self.lock = threading.Lock()
        self.registry = registry or RoomRegistry()

    def create_room(self, host_ip: str, host_port: int, duration: int) -> Room:
        room = Room(host_ip, host_port, duration)
        with self.lock:
            self.rooms[room.room_id] = room
        expires_at = room.start_time + room.duration
        self.registry.register_room(room.room_id, host_ip, host_port, expires_at)
        threading.Thread(target=self._room_timer, args=(room,), daemon=True).start()
        return room

    def get_room(self, room_id: str) -> Optional[Room]:
        with self.lock:
            room = self.rooms.get(room_id)
            if room is not None:
                return room
        room_info = self.registry.get_room(room_id)
        if room_info is None:
            return None
        room = Room(
            host_ip=room_info["host_ip"],
            host_port=room_info["host_port"],
            duration=0 # Duration unknown for registry-loaded rooms
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
