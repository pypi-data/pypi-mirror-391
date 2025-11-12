import json
import random
import threading
from socket import socket

from nacl.public import PublicKey
from nacl.signing import SigningKey, VerifyKey

from core.globals import running
from core.networking.peer_connection import PeerConnection
from core.networking.peer_crypto import PeerCrypto
from core.networking.peer_events import PeerEvents
from core.networking.peer_state import PeerState
from core.storage.user_manager import UserManager
from core.debug.debugging import log
from core.utils.listener import Listener


class Peer:
    def __init__(self, network_manager, user_manager: UserManager, conn, addr, my_sign: SigningKey, get_trusted_token):
        self.network_manager = network_manager
        self.user_manager = user_manager
        self.conn = conn
        self.addr = addr

        self.listener = Listener(["connected", "message_received", "message_sent"])

        self.peer_state = PeerState(user_manager, my_sign)
        self.peer_crypto = PeerCrypto(self.peer_state, get_trusted_token)
        self.peer_events = PeerEvents(self.disconnect, self.listener, self.peer_state)
        self.peer_connection = PeerConnection(self.disconnect, self.peer_crypto, self.conn, self.peer_events)

        self._disconnected = False
        log("new peer created with random debug number of: " + str(random.randrange(1000, 9999)))
        self.start()

    def start(self):
        threading.Thread(target=self.listen_for_connection_information, daemon=True).start()

        self.conn.sendall(self._get_connection_string())

    def _get_connection_string(self):
        payload = {
            "type": "connection".encode().hex(),
            "encryption_key": bytes(self.peer_crypto.my_pk).hex(),
            "signature": self.peer_crypto.my_signing_key.sign(bytes(self.peer_crypto.my_pk)).signature.hex(),
            "verify_key": bytes(self.peer_crypto.my_verify_key).hex(),
            "trusted_token_exists": bool(self.peer_state.my_information.get("trusted_token"))
        }

        return json.dumps(payload).encode()

    def listen_for_connection_information(self):
        while running and not self._disconnected and not self.peer_state.peer_information.get("verify_key"):
            data = self.peer_connection.receive()

            peer_encryption_key = bytes.fromhex(data["encryption_key"])
            peer_signature = bytes.fromhex(data["signature"])
            peer_verify_key = VerifyKey(bytes.fromhex(data["verify_key"]))
            peer_trusted_token_exists = bool(data["trusted_token_exists"])

            peer_verify_key.verify(peer_encryption_key, peer_signature)

            peer_pk = PublicKey(peer_encryption_key)
            self.peer_crypto.set_my_box(peer_pk)
            self.peer_state.update_peer(peer_verify_key, peer_pk, peer_trusted_token_exists)

            self.peer_state.connected = True

            self.peer_state.reload_user_information()
            self.peer_state.resolve_trusted_state()

        log(self.peer_state.peer_information.get("verify_key"))

        threading.Thread(target=self.listen_for_events, daemon=True).start()

    def listen_for_events(self):
        log("listening for events")
        log(self.conn)

        while running and not self._disconnected:
            event = self.peer_connection.receive()
            log(event)
            self.peer_events.on_event_received(event)

        self.disconnect("listen_for_events: no longer running")

    def disconnect(self, reason=None):
        log("disconnecting for : " + str(reason))

        if self._disconnected:
            return
        self._disconnected = True

        # send disconnect only if socket is still valid
        try:
            if self.conn and isinstance(self.conn, socket):
                self.peer_connection.send_disconnect()
        except OSError:
            pass

        try:
            if self.conn and isinstance(self.conn, socket):
                self.conn.close()
        except OSError:
            pass

        self.network_manager.remove_peer(self, reason)
