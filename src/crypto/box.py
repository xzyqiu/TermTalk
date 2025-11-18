import hmac
import hashlib
import base64
from typing import Union


class SecureBox:
    """Lightweight HMAC-based secure envelope.

    This class provides simple symmetric 'encrypt'/'decrypt' operations by
    appending an HMAC-SHA256 to the plaintext and Base64-encoding the result.
    It's intentionally simple and *not* a replacement for authenticated
    encryption algorithms (e.g., AES-GCM) in production.
    """

    def __init__(self, key: Union[str, bytes]):
        if isinstance(key, str):
            key = key.encode()
        self.key: bytes = key

    def encrypt(self, message: str) -> str:
        """Return Base64-encoded plaintext || HMAC-SHA256."""
        msg_bytes = message.encode()
        mac = hmac.new(self.key, msg_bytes, hashlib.sha256).digest()
        return base64.b64encode(msg_bytes + mac).decode()

    def decrypt(self, encrypted_msg: str) -> str:
        """Verify HMAC and return original plaintext or raise ValueError."""
        decoded = base64.b64decode(encrypted_msg.encode())
        if len(decoded) < 32:
            raise ValueError("Encrypted payload too short")
        msg, received_hmac = decoded[:-32], decoded[-32:]
        expected_hmac = hmac.new(self.key, msg, hashlib.sha256).digest()
        if not hmac.compare_digest(received_hmac, expected_hmac):
            raise ValueError("Message integrity check failed")
        return msg.decode()
