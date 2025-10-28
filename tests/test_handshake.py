import unittest
from src.crypto.handshake import Handshake
from src.crypto.box import SecureBox

class TestHandshake(unittest.TestCase):
    def test_shared_box_generation(self):
        alice = Handshake()
        bob = Handshake()

        shared_key_alice = alice.generate_shared_box(bob.key)
        shared_key_bob = bob.generate_shared_box(alice.key)

        self.assertEqual(shared_key_alice, shared_key_bob)

        box = SecureBox(shared_key_alice)
        message = "Secret handshake"
        encrypted = box.encrypt(message)
        decrypted = box.decrypt(encrypted)
        self.assertEqual(message, decrypted)

if __name__ == "__main__":
    unittest.main()
