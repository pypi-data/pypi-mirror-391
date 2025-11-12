import json
import threading

from nacl.public import PublicKey, Box
from nacl.signing import VerifyKey

import core.globals
from core.networking.peer_crypto import PeerCrypto


class PeerConnection:
    def __init__(self, disconnect, crypto: PeerCrypto, conn, peer_events):
        self.peer_events = peer_events
        self.disconnect = disconnect

        self.crypto = crypto
        self.conn = conn

    def _send(self, message: dict, encrypt=True):
        data = json.dumps(message).encode()
        if encrypt and self.crypto.box:
            data = self.crypto.box.encrypt(data)

        try:
            self.conn.sendall(data)
        except (ConnectionError, OSError) as e:
            self.disconnect("_send failed: " + str(e))

    def receive(self, decrypt=True, buffer=4096):
        try:
            data = self.conn.recv(buffer)
            if not data:
                return None
            if decrypt and self.crypto.box:
                data = self.crypto.box.decrypt(data)
            return json.loads(data.decode())
        except (ConnectionError, OSError) as e:
            self.disconnect("receive failed: " + str(e))

    def send_message(self, message):
        payload = {"type": "message_received", "message": message}
        self._send(payload)
        self.peer_events.on_event_received({ "type": "message_sent", "message": message })

    def send_disconnect(self):
        payload = {"type": "disconnect"}
        self._send(payload)