import unittest
import os
import base64
from src.crypto.box import SecureBox


class TestSecureBox(unittest.TestCase):
    def test_encrypt_decrypt(self):
        # Use a proper 32-byte key
        key = os.urandom(32)
        box = SecureBox(key)
        message = "Hello, secure world!"
        encrypted = box.encrypt(message)
        decrypted = box.decrypt(encrypted)
        self.assertEqual(message, decrypted)

    def test_tampered_message(self):
        key = os.urandom(32)
        box = SecureBox(key)
        message = "Test message"
        encrypted = box.encrypt(message)

        # Tamper with message
        tampered = encrypted[:-4] + "abcd"
        with self.assertRaises(ValueError):
            box.decrypt(tampered)
    
    def test_invalid_key_length(self):
        """Test that invalid key length raises error"""
        with self.assertRaises(ValueError):
            SecureBox(b"tooshort")
    
    def test_different_nonces(self):
        """Test that same message produces different ciphertexts (due to random nonce)"""
        key = os.urandom(32)
        box = SecureBox(key)
        message = "Test message"
        encrypted1 = box.encrypt(message)
        encrypted2 = box.encrypt(message)
        # Same message should produce different ciphertexts
        self.assertNotEqual(encrypted1, encrypted2)
        # But both should decrypt to same plaintext
        self.assertEqual(box.decrypt(encrypted1), message)
        self.assertEqual(box.decrypt(encrypted2), message)


if __name__ == "__main__":
    unittest.main()
