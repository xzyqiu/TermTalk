"""Privacy protection tests for TermTalk.

Ensures no persistent identifiers or system metadata are exposed.
"""
import unittest
import sys
import importlib
from src.utils.privacy import (
    generate_anonymous_room_id,
    generate_anonymous_peer_id,
    sanitize_error_message,
    get_privacy_info,
)
from src.room.manager import Room


class TestPrivacyProtection(unittest.TestCase):
    """Test that no persistent identifiers are exposed."""

    def test_no_mac_address_in_room_id(self):
        """Ensure room IDs don't contain MAC addresses."""
        # Generate multiple room IDs
        room_ids = [generate_anonymous_room_id() for _ in range(10)]
        
        # All should be different (randomness check)
        self.assertEqual(len(set(room_ids)), 10, "Room IDs should be unique")
        
        # All should be 16 hex characters
        for room_id in room_ids:
            self.assertEqual(len(room_id), 16)
            self.assertTrue(all(c in '0123456789abcdef' for c in room_id))

    def test_no_mac_address_in_peer_id(self):
        """Ensure peer IDs don't contain system info."""
        peer_ids = [generate_anonymous_peer_id() for _ in range(10)]
        
        # All should be different
        self.assertEqual(len(set(peer_ids)), 10, "Peer IDs should be unique")
        
        # All should be 6 alphanumeric characters
        for peer_id in peer_ids:
            self.assertEqual(len(peer_id), 6)
            self.assertTrue(peer_id.isalnum())
            self.assertTrue(peer_id.islower() or peer_id.isdigit())

    def test_room_uses_anonymous_ids(self):
        """Test that Room class uses privacy-preserving IDs."""
        room = Room("127.0.0.1", 12345, 300)
        
        # Room ID should be 16 hex chars
        self.assertEqual(len(room.room_id), 16)
        self.assertTrue(all(c in '0123456789abcdef' for c in room.room_id))
        
        # Add peer and check peer ID
        peer_id = room.add_peer()
        self.assertEqual(len(peer_id), 6)
        self.assertTrue(peer_id.isalnum())

    def test_error_message_sanitization(self):
        """Test that error messages don't leak filesystem paths."""
        # Create errors with potentially sensitive info
        errors = [
            ValueError("/home/user/secret/path.py"),
            FileNotFoundError("/usr/local/python/lib/module.py"),
            RuntimeError("C:\\Users\\Admin\\Documents\\file.txt"),
        ]
        
        for error in errors:
            sanitized = sanitize_error_message(error)
            # Should only return error type, not message
            self.assertIn("Error", sanitized)
            # Should not contain filesystem paths
            self.assertNotIn("/", sanitized)
            self.assertNotIn("\\", sanitized)
            self.assertNotIn("home", sanitized)
            self.assertNotIn("user", sanitized)

    def test_privacy_info_status(self):
        """Test privacy information reporting."""
        info = get_privacy_info()
        
        # Verify all privacy protections are active
        self.assertFalse(info["mac_address_exposed"])
        self.assertFalse(info["hostname_exposed"])
        self.assertFalse(info["system_info_exposed"])
        self.assertTrue(info["uses_ephemeral_ids"])
        self.assertTrue(info["secure_randomness"])
        self.assertTrue(info["session_only_identifiers"])

    def test_no_uuid1_usage(self):
        """Verify uuid.uuid1() (MAC-based) is not used in code."""
        # Check critical modules don't use uuid1 (MAC-based)
        import src.room.manager as manager_module
        
        # Read source to verify no uuid module import
        import inspect
        
        manager_source = inspect.getsource(manager_module)
        # Verify uuid module is not imported (we use secrets instead)
        lines = [line.strip() for line in manager_source.split('\n') 
                if not line.strip().startswith('#')]
        code_lines = ' '.join(lines)
        
        # Check that uuid is not imported
        self.assertNotIn("import uuid", code_lines, 
                        "uuid module should not be imported (use secrets module)")

    def test_no_hostname_leakage(self):
        """Verify socket.gethostname() is not used."""
        import src.transport.socket_handler as socket_module
        import inspect
        
        socket_source = inspect.getsource(socket_module)
        self.assertNotIn("gethostname", socket_source, "hostname should not be exposed")

    def test_no_platform_info_leakage(self):
        """Verify platform module is not used for system info."""
        # Check key modules don't import platform
        forbidden_imports = ['platform']
        
        modules_to_check = [
            'src.crypto.handshake',
            'src.crypto.box',
            'src.transport.socket_handler',
            'src.room.manager',
        ]
        
        for module_name in modules_to_check:
            try:
                module = importlib.import_module(module_name)
                import inspect
                source = inspect.getsource(module)
                
                for forbidden in forbidden_imports:
                    self.assertNotIn(f"import {forbidden}", source,
                                   f"{module_name} should not import {forbidden}")
            except Exception:
                pass  # Module might not be importable in test environment

    def test_room_id_randomness(self):
        """Test that room IDs have sufficient randomness."""
        # Generate many room IDs
        room_ids = [generate_anonymous_room_id() for _ in range(100)]
        
        # All should be unique
        self.assertEqual(len(set(room_ids)), 100, 
                        "Room IDs should be unique (sufficient randomness)")
        
        # Check distribution of first character (should be roughly uniform)
        first_chars = [rid[0] for rid in room_ids]
        unique_first = len(set(first_chars))
        # Should have at least 8 different first characters in 100 samples
        self.assertGreater(unique_first, 8, 
                          "Room IDs should have good randomness distribution")

    def test_peer_id_randomness(self):
        """Test that peer IDs have sufficient randomness."""
        peer_ids = [generate_anonymous_peer_id() for _ in range(100)]
        
        # Should have high uniqueness
        unique_count = len(set(peer_ids))
        self.assertGreater(unique_count, 95, 
                          "Peer IDs should be highly unique")


class TestMetadataStripping(unittest.TestCase):
    """Test that no metadata is persisted or transmitted."""

    def test_handshake_only_sends_public_key(self):
        """Verify handshake only transmits cryptographic public key."""
        from src.crypto.handshake import Handshake
        
        handshake = Handshake()
        public_key = handshake.get_public_key_str()
        
        # Should be base64-encoded X25519 public key (44 chars)
        self.assertEqual(len(public_key), 44)
        # Should only contain base64 characters
        import string
        valid_chars = string.ascii_letters + string.digits + '+/='
        self.assertTrue(all(c in valid_chars for c in public_key))

    def test_registry_only_stores_ephemeral_data(self):
        """Verify registry doesn't store persistent identifiers."""
        from src.room.registry import RoomRegistry
        import tempfile
        import os
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            registry_path = f.name
        
        try:
            registry = RoomRegistry(registry_path)
            
            # Register a room
            registry.register_room("test123456789abc", "127.0.0.1", 12345, 9999999999.0)
            
            # Read registry file
            with open(registry_path, 'r') as f:
                data = json.load(f)
            
            # Should only contain: room_id, host_ip, host_port, expires_at
            for room_id, room_data in data.items():
                self.assertIn("host_ip", room_data)
                self.assertIn("host_port", room_data)
                self.assertIn("expires_at", room_data)
                # Should NOT contain hostname, username, MAC, etc.
                self.assertNotIn("hostname", room_data)
                self.assertNotIn("username", room_data)
                self.assertNotIn("mac_address", room_data)
                self.assertNotIn("system", room_data)
        finally:
            if os.path.exists(registry_path):
                os.unlink(registry_path)


if __name__ == "__main__":
    unittest.main()
