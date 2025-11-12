import socket
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor

import core.globals
from core.globals import VERSION
from core.debug.debugging import log
from core.networking.network_manager import NetworkManager
from core.storage.credentials_manager import CredentialsManager
from core.storage.user_manager import UserManager


class DiscoveryManager:
    def __init__(self, credentials_manager: CredentialsManager, user_manager: UserManager, network_manager: NetworkManager, max_broadcast_number):
        self.broadcast_port = core.globals.BROADCAST_PORT
        self.verify_key = credentials_manager.get_signing_key().verify_key
        self.listen_addr = network_manager.listen_sock.getsockname()

        self.user_manager = user_manager
        self.max_broadcast_number = max_broadcast_number

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # do NOT allow this for real
        sock.bind((socket.gethostbyname(socket.gethostname()), self.broadcast_port))

        self.sock = sock

        self.broadcast_executor = ThreadPoolExecutor(max_workers=1)
        self.listen_executor = ThreadPoolExecutor(max_workers=1)

        self.replied_to = set()
        self.reply_timeout = 3


    def get_broadcast_string(self, disconnect=False):
        return f"NOTEPASSER|{VERSION}|{bytes(self.verify_key).hex()}|{self.listen_addr[0]}|{self.listen_addr[1]}|{'DISCONNECT' if disconnect else 'CONNECT'}"

    def start_broadcast(self):
        def broadcast():
            log("discovery broadcast started")
            self.user_manager.set_discovered([])
            for i in range(0, self.max_broadcast_number):
                message = self.get_broadcast_string()
                log("sending discovery packet " + message)
                self.sock.sendto(message.encode("utf-8"), ("255.255.255.255", self.broadcast_port))
                time.sleep(1.5)

        self.broadcast_executor.submit(broadcast)

    def start_listening(self):
        def listen():
             log("discovery listen started")
             while True:
                 try:
                     data, addr = self.sock.recvfrom(4096)
                     text = data.decode("utf-8", errors="replace").split("|")
                     if len(text) != 6:
                         log("discovered invalid user")
                         continue
                     prefix, version, peer_verify_key, ip, port, disconnect = text
                     disconnect = disconnect == "DISCONNECT"
                     peer_addr = (ip, int(port))
                     peer_verify_key = bytes.fromhex(peer_verify_key)
                     if prefix != "NOTEPASSER" or version != VERSION:
                         log("different version or irrelevant packet")
                         continue
                     if peer_verify_key == bytes(self.verify_key):
                         log("discovered self")
                         continue
                     log("discovered user " + peer_verify_key.hex() + " with address " + str(peer_addr))

                     self.user_manager.on_user_discovered(peer_verify_key, peer_addr, disconnect)
                     if not disconnect: self.respond_to_discovery_request(peer_verify_key)
                 except socket.timeout:
                     continue
                 except ConnectionResetError:
                     log("windows badness")
                     continue

        self.listen_executor.submit(listen)

    def respond_to_discovery_request(self, peer_verify_key):
        if peer_verify_key in self.replied_to: return
        log("sending discovery packet")
        self.sock.sendto(self.get_broadcast_string().encode("utf-8"), ("255.255.255.255", self.broadcast_port)) # this should really have some kind of limiter
        self.replied_to.add(peer_verify_key)
        self.remove_from_replied_to_after_delay(peer_verify_key)

    def remove_from_replied_to_after_delay(self, peer_verify_key):
        def remove():
            nonlocal peer_verify_key
            time.sleep(self.reply_timeout)
            if not peer_verify_key in self.replied_to: return
            self.replied_to.remove(peer_verify_key)

        threading.Thread(target=remove, daemon=True).start()

    def stop(self):
        self.stop_broadcasting()
        self.listen_executor.shutdown(wait=False)
        message = self.get_broadcast_string(disconnect=True)
        log("shutting down: ", message)
        self.sock.sendto(message.encode('utf-8'), ("255.255.255.255", self.broadcast_port))

    def stop_broadcasting(self): self.broadcast_executor.shutdown(wait=False)
