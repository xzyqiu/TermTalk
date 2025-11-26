import base64
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization


class Handshake:
    """Secure handshake using X25519 ECDH key exchange.

    This class generates an ephemeral X25519 key pair and performs
    Diffie-Hellman key exchange to derive a shared symmetric session key
    using HKDF for proper key derivation. Provides forward secrecy.
    """

    def __init__(self, private_key: Optional[X25519PrivateKey] = None):
        """Initialize handshake with optional private key (mainly for testing)."""
        self.private_key = private_key or X25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def get_public_key_str(self) -> str:
        """Return base64-encoded public key bytes for transmission."""
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return base64.b64encode(public_bytes).decode('ascii')

    def generate_shared_box(self, peer_key_str: str) -> bytes:
        """Derive shared secret from peer's public key using ECDH + HKDF.
        
        Args:
            peer_key_str: Base64-encoded peer public key
            
        Returns:
            32-byte shared secret suitable for use as encryption key
        """
        # Decode peer's public key
        peer_key_bytes = base64.b64decode(peer_key_str.encode('ascii'))
        peer_public_key = X25519PublicKey.from_public_bytes(peer_key_bytes)
        
        # Perform ECDH to get shared secret
        shared_secret = self.private_key.exchange(peer_public_key)
        
        # Derive key material using HKDF
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'TermTalk v1 session key',
        ).derive(shared_secret)
        
        return derived_key
