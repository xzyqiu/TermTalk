import threading
import time
import uuid
from typing import Dict, Optional


class Room:
    """Represents a hosted room with peer bookkeeping and TTL.

    Attributes are intentionally small for testing. `peers` maps peer_id
    strings to optional metadata.
    """

    def __init__(self, host_ip: str, host_port: int, duration: int):
        self.room_id = str(uuid.uuid4())[:8]
        self.host_ip = host_ip
        self.host_port = host_port
        self.duration = duration
        self.start_time = time.time()
        self.active = True
        self.peers: Dict[str, dict] = {}

    def add_peer(self, peer_info: Optional[dict] = None) -> str:
        peer_id = str(uuid.uuid4())[:6]
        self.peers[peer_id] = peer_info or {}
        return peer_id

    def remove_peer(self, peer_id: str) -> None:
        self.peers.pop(peer_id, None)

    def check_expiry(self) -> bool:
        if time.time() - self.start_time >= self.duration:
            self.active = False
        return self.active


class RoomManager:
    """Thread-safe manager for rooms. Rooms self-expire on a background thread."""

    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.lock = threading.Lock()

    def create_room(self, host_ip: str, host_port: int, duration: int) -> Room:
        room = Room(host_ip, host_port, duration)
        with self.lock:
            self.rooms[room.room_id] = room
        threading.Thread(target=self._room_timer, args=(room,), daemon=True).start()
        return room

    def get_room(self, room_id: str) -> Optional[Room]:
        with self.lock:
            return self.rooms.get(room_id)

    def remove_room(self, room_id: str) -> None:
        with self.lock:
            self.rooms.pop(room_id, None)

    def _room_timer(self, room: Room) -> None:
        while room.active:
            time.sleep(1)
            room.check_expiry()
        print(f"[ROOM] Room {room.room_id} expired")
        host_socket = getattr(room, "host_socket", None)
        # Stop host socket if it provides a stop() method
        if host_socket is not None and hasattr(host_socket, "stop"):
            try:
                host_socket.stop()
            except Exception:
                pass
        self.remove_room(room.room_id)
