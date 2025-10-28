import hmac
import hashlib
import base64

class SecureBox:
    def __init__(self, key):
        self.key = key.encode()

    def encrypt(self, message: str) -> str:
        msg_bytes = message.encode()
        h = hmac.new(self.key, msg_bytes, hashlib.sha256).digest()
        encrypted = base64.b64encode(msg_bytes + h).decode()
        return encrypted

    def decrypt(self, encrypted_msg: str) -> str:
        decoded = base64.b64decode(encrypted_msg.encode())
        msg, received_hmac = decoded[:-32], decoded[-32:]
        expected_hmac = hmac.new(self.key, msg, hashlib.sha256).digest()
        if not hmac.compare_digest(received_hmac, expected_hmac):
            raise ValueError("Message integrity check failed")
        return msg.decode()
