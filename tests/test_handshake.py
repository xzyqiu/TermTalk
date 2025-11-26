import unittest
from src.crypto.handshake import Handshake
from src.crypto.box import SecureBox

class TestHandshake(unittest.TestCase):
    def test_shared_box_generation(self):
        alice = Handshake()
        bob = Handshake()

        # Exchange public keys
        alice_public = alice.get_public_key_str()
        bob_public = bob.get_public_key_str()

        # Generate shared keys
        shared_key_alice = alice.generate_shared_box(bob_public)
        shared_key_bob = bob.generate_shared_box(alice_public)

        # Keys should be identical
        self.assertEqual(shared_key_alice, shared_key_bob)

        # Test encryption with derived key
        box = SecureBox(shared_key_alice)
        message = "Secret handshake"
        encrypted = box.encrypt(message)
        decrypted = box.decrypt(encrypted)
        self.assertEqual(message, decrypted)

if __name__ == "__main__":
    unittest.main()
