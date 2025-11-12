from core.networking.discovery_manager import DiscoveryManager
from core.networking.network_manager import NetworkManager
from core.storage.credentials_manager import CredentialsManager
from core.storage.storage_manager import StorageManager
from core.storage.user_manager import UserManager


class Node:
    def __init__(self, get_trusted_token_input, config_dir=".notepasser"):
        self.storage_manager = StorageManager(config_dir)
        self.user_manager = UserManager(self.storage_manager)
        self.credentials_manager = CredentialsManager(self.storage_manager)

        self.network_manager = NetworkManager(self.credentials_manager, self.user_manager, get_trusted_token_input)
        self.discovery_manager = DiscoveryManager(self.credentials_manager, self.user_manager, self.network_manager, 3)

        self.discovery_manager.start_listening()
        self.discovery_manager.start_broadcast()
