import uuid

class Handshake:
    def __init__(self, key=None):
        self.key = key or str(uuid.uuid4())[:32]

    def get_public_key_str(self):
        return self.key

    def generate_shared_box(self, peer_key):
        combined = "".join(sorted([self.key, peer_key]))
        return combined[:32]
