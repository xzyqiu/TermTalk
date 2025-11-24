"""Simple file-based room registry for cross-process discovery.

This is a minimal implementation for local testing/demo. For production,
replace with a proper distributed registry (Redis, etcd, or HTTP service).
"""
import json
import os
import threading
from pathlib import Path
from typing import Optional, Dict


class RoomRegistry:
    """File-based registry for sharing room info across processes."""
    
    def __init__(self, registry_path: Optional[str] = None):
        if registry_path is None:
            registry_path = os.path.join(os.path.expanduser("~"), ".termtalk_rooms.json")
        self.registry_path = Path(registry_path)
        self.lock = threading.Lock()
        
    def register_room(self, room_id: str, host_ip: str, host_port: int, expires_at: float) -> None:
        """Register a room in the file-based registry."""
        with self.lock:
            rooms = self._read_registry()
            rooms[room_id] = {
                "host_ip": host_ip,
                "host_port": host_port,
                "expires_at": expires_at
            }
            self._write_registry(rooms)
    
    def get_room(self, room_id: str) -> Optional[Dict]:
        """Get room info from registry, returns None if not found or expired."""
        import time
        with self.lock:
            rooms = self._read_registry()
            room_info = rooms.get(room_id)
            if room_info is None:
                return None
            # Check if expired
            if time.time() > room_info.get("expires_at", 0):
                # Clean up expired room
                del rooms[room_id]
                self._write_registry(rooms)
                return None
            return room_info
    
    def unregister_room(self, room_id: str) -> None:
        """Remove a room from the registry."""
        with self.lock:
            rooms = self._read_registry()
            if room_id in rooms:
                del rooms[room_id]
                self._write_registry(rooms)
    
    def _read_registry(self) -> Dict:
        """Read the registry file, return empty dict if doesn't exist."""
        if not self.registry_path.exists():
            return {}
        try:
            with open(self.registry_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _write_registry(self, rooms: Dict) -> None:
        """Write the registry file."""
        try:
            with open(self.registry_path, "w") as f:
                json.dump(rooms, f, indent=2)
        except IOError:
            pass  # Fail silently for demo purposes
