import socket
import threading
import time
import traceback

from core.storage.credentials_manager import CredentialsManager
from core.globals import running
from core.networking.peer import Peer
from core.storage.user_manager import UserManager
from core.debug.debugging import log


class NetworkManager:
    def __init__(self, credentials_manager: CredentialsManager, user_manager: UserManager, get_trusted_token_input):
        self.credentials_manager = credentials_manager
        self.user_manager = user_manager
        self.get_trusted_token_input = get_trusted_token_input
        self.peers = {}
        self.peers_lock = threading.Lock()

        listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_sock.bind((socket.gethostbyname(socket.gethostname()), 0))
        listen_sock.listen(5)
        self.listen_sock = listen_sock

        threading.Thread(target=self.listen_for_peers, daemon=True).start()

    def listen_for_peers(self):
        while running:
            try:
                conn, addr = self.listen_sock.accept()
                log("accepted peer " + str(addr))
                if addr in self.peers:
                    log("already exists")
                    continue
                self.peers[addr] = Peer(self, self.user_manager, conn, addr, self.credentials_manager.get_signing_key(), self.get_trusted_token_input)
            except (ConnectionError, socket.timeout):
                continue

    def connect_to_peer(self, verify_key):
        user = self.user_manager.get_user(verify_key)
        peer_ip, peer_port = user.addr
        log("trying to connect to " + str(user.addr))

        # see if peer connection already established
        for peer in self.peers.values():
            timeout = 5
            start = time.time()

            while peer.peer_state.peer_information is None and time.time() - start < timeout:
                time.sleep(0.1)

            log(bytes(peer.peer_state.peer_information['verify_key']).hex(), bytes(verify_key).hex())
            if peer.peer_state.peer_information and bytes(peer.peer_state.peer_information['verify_key']).hex() == bytes(verify_key).hex():
                return peer

        # establish a new peer connection
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((peer_ip, peer_port))

            self.peers[(peer_ip, peer_port)] = Peer(self, self.user_manager, conn, (peer_ip, peer_port), self.credentials_manager.get_signing_key(), self.get_trusted_token_input)
            log("connected to " + str((peer_ip, peer_port)))
            return self.peers[(peer_ip, peer_port)]
        except Exception as e:
            log(f"error connecting to {peer_ip}:{peer_port}: {e}", traceback.format_exc())

    def remove_peer(self, peer, reason=None):
        peer.disconnect(reason)
        with self.peers_lock:
            keys_to_remove = [k for k, v in self.peers.items() if v is peer]
            for k in keys_to_remove:
                del self.peers[k]
