import json
import queue
import time

from nacl.public import PrivateKey, Box
from nacl.signing import SigningKey, VerifyKey

from core.debug.debugging import log
from core.networking.peer_state import PeerState


class PeerCrypto:
    def __init__(self, state: PeerState, get_trusted_token):
        self.state = state

        self.my_signing_key = self.state.my_signing_key
        self.my_verify_key = self.my_signing_key.verify_key
        self.my_sk = PrivateKey.generate()
        self.my_pk = self.my_sk.public_key
        self.box = None

        self.get_trusted_token = get_trusted_token

    def ensure_my_box(self):
        if not self.box: raise RuntimeError("Encryption box is not initialized")

    def encrypt_string(self, message):
        self.ensure_my_box()
        return self.box.encrypt(message.encode())

    def encrypt_json(self, json_message):
        self.ensure_my_box()
        return self.encrypt_string(json.dumps(json_message))

    def decrypt_string(self, encrypted_message):
        self.ensure_my_box()
        return self.box.decrypt(encrypted_message).decode()

    def decrypt_json(self, encrypted_message):
        self.ensure_my_box()
        return json.loads(self.decrypt_string(encrypted_message))

    def set_my_box(self, peer_public_key):
        self.box = Box(self.my_sk, peer_public_key)
