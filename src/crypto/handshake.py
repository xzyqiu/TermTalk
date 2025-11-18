import uuid
from typing import Optional


class Handshake:
    """Simple handshake helper for demo purposes.

    This intentionally lightweight class generates a short 'public key'
    (a random string) and deterministically derives a shared symmetric
    key by combining two public keys. The algorithm is for demo/testing
    only and is not secure for production use.
    """

    def __init__(self, key: Optional[str] = None):
        self.key = key or str(uuid.uuid4())[:32]

    def get_public_key_str(self) -> str:
        return self.key

    def generate_shared_box(self, peer_key: str) -> str:
        combined = "".join(sorted([self.key, peer_key]))
        return combined[:32]
