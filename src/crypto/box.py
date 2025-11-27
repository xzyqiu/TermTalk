import base64
import os
from typing import Union
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


class SecureBox:
    # this class does the encryption stuff
    def __init__(self, key: Union[str, bytes]):
        # handle string or bytes key
        if isinstance(key, str):
            key = base64.b64decode(key.encode('ascii'))
        if len(key) != 32:
            raise ValueError("Key must be exactly 32 bytes")
        
        # setup the cipher thing
        self.cipher = ChaCha20Poly1305(key)

    def encrypt(self, message: str) -> str:
        # convert message to bytes
        msg_bytes = message.encode('utf-8')
        # make random nonce
        nonce = os.urandom(12)
        # do the encryption
        ciphertext = self.cipher.encrypt(nonce, msg_bytes, None)

        # return encoded result
        return base64.b64encode(nonce + ciphertext).decode('ascii')

    def decrypt(self, encrypted_msg: str) -> str:
        # decode from base64
        try:
            decoded = base64.b64decode(encrypted_msg.encode('ascii'))
        except Exception as e:
            raise ValueError(f"Invalid base64 encoding: {e}")
        # check length
        if len(decoded) < 28:
            raise ValueError("Encrypted payload too short")
        # split nonce and ciphertext
        nonce = decoded[:12]
        ciphertext = decoded[12:]
        # try to decrypt it
        try:
            plaintext = self.cipher.decrypt(nonce, ciphertext, None)
        except Exception:
            # failed to decrypt
            raise ValueError("Message authentication failed or corrupted")
        
        # return the decrypted message
        return plaintext.decode('utf-8')
