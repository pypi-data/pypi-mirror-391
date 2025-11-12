from nacl.public import PrivateKey


class PeerState:
    def __init__(self, user_manager, my_signing_key):
        self.user_manager = user_manager

        self.my_signing_key = my_signing_key
        self.my_verify_key = self.my_signing_key.verify_key

        self.peer_information = {
            "verify_key": None,
            "public_key": None,
            "addr": None,
            "trusted_token_exists": None
        }

        self.my_information = {
            "verify_key": self.my_verify_key,
            "trusted_token": None
        }

        self.connected = False
        self.trusted = False

    def reload_user_information(self):
        self.my_information = self.user_manager.get_user(self.my_verify_key).serialize()

    def update_peer(self, peer_verify_key, peer_pk, trusted_token_exists):
        self.peer_information = {
            "verify_key": peer_verify_key,
            "public_key": peer_pk,
            "trusted_token_exists": trusted_token_exists
        }
        self.resolve_trusted_state()

    def resolve_trusted_state(self):
        me_trust_peer = bool(self.my_information.get("trusted_token"))
        peer_trust_me = self.peer_information.get("trusted_token_exists", False)
        self.trusted = me_trust_peer or peer_trust_me
