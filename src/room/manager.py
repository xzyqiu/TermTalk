import threading
import time
import uuid

class Room:
    def __init__(self, host_ip, host_port, duration):
        self.room_id = str(uuid.uuid4())[:8]
        self.host_ip = host_ip
        self.host_port = host_port
        self.duration = duration
        self.start_time = time.time()
        self.active = True
        self.peers = {}  # peer_id: info

    def add_peer(self, peer_info=None):
        peer_id = str(uuid.uuid4())[:6]
        self.peers[peer_id] = peer_info or {}
        return peer_id

    def remove_peer(self, peer_id):
        if peer_id in self.peers:
            del self.peers[peer_id]

    def check_expiry(self):
        if time.time() - self.start_time >= self.duration:
            self.active = False
        return self.active


class RoomManager:
    def __init__(self):
        self.rooms = {}
        self.lock = threading.Lock()

    def create_room(self, host_ip, host_port, duration):
        room = Room(host_ip, host_port, duration)
        with self.lock:
            self.rooms[room.room_id] = room
        threading.Thread(target=self._room_timer, args=(room,), daemon=True).start()
        return room

    def get_room(self, room_id):
        with self.lock:
            return self.rooms.get(room_id)

    def remove_room(self, room_id):
        with self.lock:
            if room_id in self.rooms:
                del self.rooms[room_id]

    def _room_timer(self, room):
        while room.active:
            time.sleep(1)
            room.check_expiry()
        print(f"[ROOM] Room {room.room_id} expired")
        if hasattr(room, "host_socket") and room.host_socket.running:
            room.host_socket.stop()
        self.remove_room(room.room_id)
