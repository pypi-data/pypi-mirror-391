from threading import Lock
from operator import lt, le, eq, ne, ge, gt


class PeerManager:
    def __init__(self):
        self.peers = {}
        self.peer_lock = Lock()
        self.ops = {
                "lt": lt,
                "le": le,
                "eq": eq,
                "ne": ne,
                "ge": ge,
                "gt": gt
            }

    def get_peers_of_state(self, comparator, level):
        if comparator not in self.ops:
            raise ValueError(f"Invalid comparator: {comparator}")

        op_func = self.ops[comparator]
        return [peer for peer in self.peers.values() if op_func(peer.peer_state, level)]

    def add_peer(self, peer):
        with self.peer_lock:
            self.peers[peer.verify_key] = peer

    def remove_peer(self, peer_verify_key):
        with self.peer_lock:
            self.peers.pop(peer_verify_key, None)
