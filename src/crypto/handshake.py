import base64
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization


class Handshake:
    # does the key exchange stuff
    def __init__(self, private_key: Optional[X25519PrivateKey] = None):
        # make or use provided private key
        self.private_key = private_key or X25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def get_public_key_str(self) -> str:
        # convert public key to string
        public_bytes = self.public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        return base64.b64encode(public_bytes).decode('ascii')

    def generate_shared_box(self, peer_key_str: str) -> bytes:
        # decode peer's public key
        peer_key_bytes = base64.b64decode(peer_key_str.encode('ascii'))
        peer_public_key = X25519PublicKey.from_public_bytes(peer_key_bytes)
        # do the key exchange to get shared secret
        shared_secret = self.private_key.exchange(peer_public_key)
        
        # derive the actual encryption key using HKDF
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'TermTalk v1 session key',
        ).derive(shared_secret)
        
        return derived_key
