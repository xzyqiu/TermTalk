import base64
import os
from typing import Union
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


class SecureBox:
    """Secure authenticated encryption using ChaCha20-Poly1305.

    This class provides authenticated encryption with associated data (AEAD)
    using the ChaCha20-Poly1305 algorithm. This ensures both confidentiality
    and integrity of messages, protecting against tampering and eavesdropping.
    """

    def __init__(self, key: Union[str, bytes]):
        """Initialize with a 32-byte key.
        
        Args:
            key: Either a 32-byte bytes object or base64-encoded string
        """
        if isinstance(key, str):
            # Assume it's base64-encoded
            key = base64.b64decode(key.encode('ascii'))
        
        if len(key) != 32:
            raise ValueError("Key must be exactly 32 bytes")
        
        self.cipher = ChaCha20Poly1305(key)

    def encrypt(self, message: str) -> str:
        """Encrypt and authenticate a message.
        
        Returns:
            Base64-encoded nonce + ciphertext + authentication tag
        """
        msg_bytes = message.encode('utf-8')
        
        # Generate a random 12-byte nonce
        nonce = os.urandom(12)
        
        # Encrypt and authenticate
        ciphertext = self.cipher.encrypt(nonce, msg_bytes, None)
        
        # Return base64-encoded nonce || ciphertext
        return base64.b64encode(nonce + ciphertext).decode('ascii')

    def decrypt(self, encrypted_msg: str) -> str:
        """Decrypt and verify a message.
        
        Args:
            encrypted_msg: Base64-encoded nonce + ciphertext + tag
            
        Returns:
            Original plaintext message
            
        Raises:
            ValueError: If authentication fails or format is invalid
        """
        try:
            decoded = base64.b64decode(encrypted_msg.encode('ascii'))
        except Exception as e:
            raise ValueError(f"Invalid base64 encoding: {e}")
        
        if len(decoded) < 28:  # 12-byte nonce + 16-byte tag minimum
            raise ValueError("Encrypted payload too short")
        
        # Split nonce and ciphertext
        nonce = decoded[:12]
        ciphertext = decoded[12:]
        
        # Decrypt and verify authentication tag
        try:
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
        except Exception:
            raise ValueError("Message authentication failed or corrupted")
        
        return plaintext.decode('utf-8')
