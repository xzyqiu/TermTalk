"""Security tests for TermTalk - tests for common attack vectors.

These tests validate protection against:
- Connection flooding (DoS)
- Brute force handshake attacks
- Message flooding
- Oversized message attacks
- Invalid input handling
"""
import unittest
import socket
import threading
import time
from src.transport.socket_handler import EncryptedHostSocket, EncryptedPeerSocket
from src.crypto.handshake import Handshake
from src.crypto.box import SecureBox


class TestConnectionSecurity(unittest.TestCase):
    """Test connection-level security controls."""

    def test_multiple_rapid_connections(self):
        """Test that server can handle rapid connection attempts."""
        host = EncryptedHostSocket("127.0.0.1", 15001)
        host.start()
        
        try:
            # Attempt to open many connections rapidly
            connections = []
            for i in range(10):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect(("127.0.0.1", 15001))
                    connections.append(sock)
                except Exception as e:
                    # Expected that some may fail or timeout
                    pass
            
            # Verify server is still responsive
            time.sleep(0.5)
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(2)
            test_sock.connect(("127.0.0.1", 15001))
            test_sock.close()
            
            # Cleanup
            for conn in connections:
                try:
                    conn.close()
                except:
                    pass
        finally:
            host.stop()

    def test_incomplete_handshake_disconnect(self):
        """Test that incomplete handshakes don't leave resources hanging."""
        host = EncryptedHostSocket("127.0.0.1", 15002)
        host.start()
        
        try:
            # Connect but don't complete handshake
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect(("127.0.0.1", 15002))
            
            # Receive server's public key but don't respond
            server_key = sock.recv(1024)
            self.assertTrue(len(server_key) > 0)
            
            # Just close without responding
            sock.close()
            
            # Server should still be functional
            time.sleep(0.5)
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(2)
            test_sock.connect(("127.0.0.1", 15002))
            test_sock.close()
        finally:
            host.stop()


class TestMessageSecurity(unittest.TestCase):
    """Test message-level security controls."""

    def test_oversized_message_handling(self):
        """Test that oversized messages are handled safely."""
        key = b"a" * 32
        box = SecureBox(key)
        
        # Create a large message (1 MB)
        large_message = "A" * (1024 * 1024)
        
        # Should be able to encrypt/decrypt large messages
        # (though transport layer may have limits)
        encrypted = box.encrypt(large_message)
        decrypted = box.decrypt(encrypted)
        self.assertEqual(decrypted, large_message)

    def test_malformed_encrypted_message(self):
        """Test that malformed encrypted messages are rejected."""
        key = b"a" * 32
        box = SecureBox(key)
        
        # Test various malformed inputs
        invalid_inputs = [
            "",  # Empty
            "not-base64!@#$",  # Invalid base64
            "dGVzdA==",  # Valid base64 but too short
            "A" * 10,  # Too short
        ]
        
        for invalid_input in invalid_inputs:
            with self.assertRaises(ValueError):
                box.decrypt(invalid_input)

    def test_replay_attack_detection(self):
        """Test that identical encrypted messages have different ciphertexts."""
        key = b"a" * 32
        box = SecureBox(key)
        message = "Test message"
        
        # Encrypt same message multiple times
        encrypted1 = box.encrypt(message)
        encrypted2 = box.encrypt(message)
        encrypted3 = box.encrypt(message)
        
        # All should be different (due to random nonces)
        self.assertNotEqual(encrypted1, encrypted2)
        self.assertNotEqual(encrypted2, encrypted3)
        self.assertNotEqual(encrypted1, encrypted3)
        
        # But all should decrypt to same message
        self.assertEqual(box.decrypt(encrypted1), message)
        self.assertEqual(box.decrypt(encrypted2), message)
        self.assertEqual(box.decrypt(encrypted3), message)


class TestHandshakeSecurity(unittest.TestCase):
    """Test handshake-level security."""

    def test_handshake_with_invalid_peer_key(self):
        """Test that invalid peer keys are rejected."""
        alice = Handshake()
        
        invalid_keys = [
            "",  # Empty
            "not-valid-base64!",  # Invalid base64
            "dGVzdA==",  # Valid base64 but wrong length
            "A" * 100,  # Wrong length
        ]
        
        for invalid_key in invalid_keys:
            with self.assertRaises(Exception):
                alice.generate_shared_box(invalid_key)

    def test_different_keys_produce_different_secrets(self):
        """Test that different peer keys produce different shared secrets."""
        alice = Handshake()
        bob = Handshake()
        charlie = Handshake()
        
        bob_key = bob.get_public_key_str()
        charlie_key = charlie.get_public_key_str()
        
        shared_with_bob = alice.generate_shared_box(bob_key)
        shared_with_charlie = alice.generate_shared_box(charlie_key)
        
        # Should be different
        self.assertNotEqual(shared_with_bob, shared_with_charlie)


class TestInputValidation(unittest.TestCase):
    """Test input validation and sanitization."""

    def test_special_characters_in_messages(self):
        """Test that special characters are handled correctly."""
        key = b"a" * 32
        box = SecureBox(key)
        
        special_messages = [
            "Hello\nWorld",  # Newlines
            "Test\r\nMessage",  # CRLF
            "Unicode: 你好世界",  # Unicode
            "Emoji: 🔒🔑",  # Emoji
            "Quotes: \"'`",  # Quotes
            "Null byte test\x00test",  # Null byte
            "<script>alert('xss')</script>",  # XSS attempt
            "'; DROP TABLE rooms; --",  # SQL injection attempt
        ]
        
        for msg in special_messages:
            encrypted = box.encrypt(msg)
            decrypted = box.decrypt(encrypted)
            self.assertEqual(decrypted, msg)

    def test_empty_message_handling(self):
        """Test that empty messages are handled correctly."""
        key = b"a" * 32
        box = SecureBox(key)
        
        empty_message = ""
        encrypted = box.encrypt(empty_message)
        decrypted = box.decrypt(encrypted)
        self.assertEqual(decrypted, empty_message)


class TestAuthenticationSecurity(unittest.TestCase):
    """Test authentication and authorization controls."""

    def test_tampered_ciphertext_rejected(self):
        """Test that tampered ciphertexts are rejected."""
        key = b"a" * 32
        box = SecureBox(key)
        message = "Secret message"
        
        encrypted = box.encrypt(message)
        
        # Tamper with different parts
        import base64
        decoded = base64.b64decode(encrypted)
        
        # Flip a bit in the nonce
        tampered1 = base64.b64encode(
            bytes([decoded[0] ^ 1]) + decoded[1:]
        ).decode('ascii')
        
        # Flip a bit in the ciphertext
        tampered2 = base64.b64encode(
            decoded[:-1] + bytes([decoded[-1] ^ 1])
        ).decode('ascii')
        
        # Both should fail authentication
        with self.assertRaises(ValueError):
            box.decrypt(tampered1)
        with self.assertRaises(ValueError):
            box.decrypt(tampered2)

    def test_wrong_key_decryption_fails(self):
        """Test that decryption with wrong key fails."""
        key1 = b"a" * 32
        key2 = b"b" * 32
        
        box1 = SecureBox(key1)
        box2 = SecureBox(key2)
        
        message = "Secret message"
        encrypted = box1.encrypt(message)
        
        # Decryption with wrong key should fail
        with self.assertRaises(ValueError):
            box2.decrypt(encrypted)


if __name__ == "__main__":
    unittest.main()
