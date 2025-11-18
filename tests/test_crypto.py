import unittest
from src.crypto.box import SecureBox
import unittest
from src.crypto.box import SecureBox


class TestSecureBox(unittest.TestCase):
    def test_encrypt_decrypt(self):
        key = "supersecretkey123"
        box = SecureBox(key)
        message = "Hello, secure world!"
        encrypted = box.encrypt(message)
        decrypted = box.decrypt(encrypted)
        self.assertEqual(message, decrypted)

    def test_tampered_message(self):
        key = "supersecretkey123"
        box = SecureBox(key)
        message = "Test message"
        encrypted = box.encrypt(message)

        # Tamper with message
        tampered = encrypted[:-4] + "abcd"
        with self.assertRaises(ValueError):
            box.decrypt(tampered)


if __name__ == "__main__":
    unittest.main()
