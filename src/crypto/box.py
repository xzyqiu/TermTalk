import base64
import os
from typing import Union
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


class SecureBox:

    def __init__(self, key: Union[str, bytes]):
        if isinstance(key, str):
            key = base64.b64decode(key.encode('ascii'))
        if len(key) != 32:
            raise ValueError("Key must be exactly 32 bytes")
        
        self.cipher = ChaCha20Poly1305(key)

    def encrypt(self, message: str) -> str:
        msg_bytes = message.encode('utf-8')
        nonce = os.urandom(12)
        ciphertext = self.cipher.encrypt(nonce, msg_bytes, None)

        return base64.b64encode(nonce + ciphertext).decode('ascii')

    def decrypt(self, encrypted_msg: str) -> str:
        try:
            decoded = base64.b64decode(encrypted_msg.encode('ascii'))
        except Exception as e:
            raise ValueError(f"Invalid base64 encoding: {e}")
        if len(decoded) < 28:
            raise ValueError("Encrypted payload too short")
        nonce = decoded[:12]
        ciphertext = decoded[12:]
        try:
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
        except Exception:
            raise ValueError("Message authentication failed or corrupted")
        
        return plaintext.decode('utf-8')
