import unittest
import time
from src.room.manager import RoomManager

class TestRoomManager(unittest.TestCase):
    def test_room_creation_and_expiry(self):
        manager = RoomManager()
        room = manager.create_room("127.0.0.1", 12345, duration=2)
        self.assertTrue(room.active)
        self.assertIn(room.room_id, manager.rooms)

        # Wait for room to expire
        time.sleep(3)
        self.assertFalse(room.active)
        self.assertNotIn(room.room_id, manager.rooms)

    def test_add_remove_peer(self):
        manager = RoomManager()
        room = manager.create_room("127.0.0.1", 12345, duration=5)
        peer_id = room.add_peer()
        self.assertIn(peer_id, room.peers)

        room.remove_peer(peer_id)
        self.assertNotIn(peer_id, room.peers)

if __name__ == "__main__":
    unittest.main()
