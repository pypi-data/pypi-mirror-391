import socket
import time

from nacl.signing import SigningKey

import core.globals
from core.networking.discovery_manager import DiscoveryManager


class MockUserManager:
    def __init__(self):
        self.discovered = []
    def set_discovered(self, users):
        print("set_discovered called:", users)
        self.discovered = users
    def on_user_discovered(self, verify_key, addr):
        print(f"discovered user {verify_key.hex()} at {addr}")
        self.discovered.append((verify_key, addr))

um1 = MockUserManager()
um2 = MockUserManager()

vkey1 = SigningKey.generate().verify_key
vkey2 = SigningKey.generate().verify_key

sock1 = socket.socket()
sock1.bind(('', 0))

sock2 = socket.socket()
sock2.bind(('', 0))

dm1 = DiscoveryManager(vkey1, um1, 3)
dm2 = DiscoveryManager(vkey2, um2, 3)

dm1.start_listening()
dm2.start_listening()

def test_discovery_succeeds():
    dm1.start_listening()
    dm2.start_listening()
    dm1.start_broadcast()
    dm2.start_broadcast()
    time.sleep(3)
    assert len(um1.discovered) > 0
    assert len(um2.discovered) > 0
