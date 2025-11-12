import socket
import threading
import time

import core.globals
from core.networking.discovery_manager import DiscoveryManager
from core.networking.network_manager import NetworkManager
from core.storage.credentials_manager import CredentialsManager
from core.storage.storage_manager import StorageManager
from core.storage.user_manager import UserManager
from core.debug.debugging import log
from core.globals import running

class Colors:
    HEADER = "\033[95m"
    ORANGE = "\033[38;5;208m"
    CYAN = "\033[96m"
    BROWN = "\033[38;5;94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_banner():
    print(f"{Colors.ORANGE}{'='*50}")
    print(f"""{Colors.YELLOW}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠞⠛⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⢀⠤⡀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⢀⡄⢧⢉⢦⠀⢻⡀⠀⠀⠀⠀⠀⣀⣤⠴⠶⣄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣞⣁⣴⣑⣪⣐⣮⣘⣀⣸⡇⠀⠀⣠⡴⠚⠉⡀⠤⡄⢸⡆⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠶⠛⢉⡁⢀⣀⠀⠀⠀⠀⠀⠉⠉⠙⠓⠾⣭⣀⠰⡍⢓⠥⠇⠈⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠃⠀⢐⢇⠼⣘⠔⣣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠃⢜⠥⠪⡇⢀⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢰⡟⣦⣄⡀⠀⠀⢿⠀⠀⠩⡌⠖⣡⢚⠊⠀⣰⡷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣧⠃⢸⠇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⣿⣾⣿⣶⣄⠘⣇⠀⠀⠈⠁⢉⣤⡀⠀⠈⠀⠀⠀⣴⡷⠀⠀⠀⠀⠀⠀⠀⠈⢧⠟⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠐⣯⢺⣿⣿⢿⣿⣷⣜⢧⡀⠀⣰⠟⣼⣇⠀⠀⠀⠀⠀⠀⠀⠀⢠⠲⢍⢏⡂⡀⠀⠘⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡎⣿⡿⣟⣿⣳⣿⣦⠙⣷⢏⣾⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⢠⢃⡎⡬⢡⣱⠀⠀⡿⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⡹⣿⣿⣻⣿⡽⣿⣧⡏⣽⣿⡿⣿⠀⢀⣤⢞⣿⠀⠀⠀⠀⠃⠜⠆⠗⠁⠀⣰⠇⠀⠀
⠀⠀⠀⠀⣀⣄⣀⣀⠀⠀⠘⣷⢻⣷⣻⣟⣿⡿⣽⣧⣿⣿⣽⣿⡴⢏⣵⣿⣿⣀⠀⠀⠀⠀⠀⠀⠀⣀⡴⠋⠀⠀⠀
⠀⠀⠀⠀⢿⡙⣭⣭⣯⣛⣶⢮⣷⣻⣿⣻⡿⣽⢿⣾⣿⣷⣿⣿⡟⠛⠛⠛⠧⣌⠙⠛⣗⠒⠒⠛⠋⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⢷⡽⣿⣻⣿⣻⣿⢿⡿⣟⣯⣿⣎⢿⣟⣯⣽⣿⣾⡀⠀⠀⠀⠀⠀⠀⠀⢻⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠙⢮⣛⢷⡿⣾⣯⢿⣿⢿⣯⠿⣯⢻⣾⣿⣷⣿⣧⡀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⢀⣴⠶⣦
⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠶⢭⣽⣿⣿⡿⣟⣿⣶⣭⠛⣾⣿⣿⣿⣽⣲⠆⠀⠀⠀⠀⢸⠃⠀⠀⠀⠀⣰⠟⠁⠀⣸
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⢞⣯⣿⣻⣽⣿⣯⣿⣿⡿⣿⣿⣿⣾⣿⠿⠿⠃⠀⠀⠀⢀⡟⠀⠀⢀⣠⠞⠁⠀⠀⣰⠏
⠀⠀⠀⠀⠀⠀⢀⣴⢏⣾⣿⣿⣯⣿⣿⣷⣻⣿⣾⣽⠟⣿⣧⠀⠀⠀⠀⠀⠀⠀⣠⣞⣠⣤⠶⠋⠁⠀⠀⢀⡼⠋⠀
⠀⠀⠀⠀⠀⠀⠈⠙⠛⠛⠛⠛⠉⠉⢰⣏⣿⡿⢿⣅⠀⢸⣿⡄⠀⠀⠀⠀⣠⡴⠋⠉⠁⠀⠀⠀⣀⣤⠶⠋⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠋⠁⠀⠀⠉⠓⠾⠿⠤⠤⠶⠖⠻⠷⠶⠤⠶⠶⠖⠚⠋⠉⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀art from https://emojicombos.com/autumn-ascii-art⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀""")
    print(f"{Colors.BOLD}{Colors.RED}        Notepasser {core.globals.VERSION} FALL UPDATE")
    print(f"{Colors.ORANGE}{'='*50}{Colors.RESET}\n")

def main(storage_location=None):
    storage = StorageManager(storage_location) if storage_location else StorageManager()
    user_manager = UserManager(storage)
    credentials = CredentialsManager(storage)

    network = NetworkManager(credentials, user_manager, input)
    discovery = DiscoveryManager(
        credentials_manager=credentials,
        user_manager=user_manager,
        network_manager=network,
        max_broadcast_number=3
    )

    discovery.start_listening()
    discovery.start_broadcast()
    print(f"{Colors.BROWN}[DISCOVERY] Listening and broadcasting started...{Colors.RESET}")

    print_banner()

    try:
        while running:
            print(f"{Colors.YELLOW}\nCOMMANDS:{Colors.RESET}")
            print(f"{Colors.ORANGE}- discover{Colors.RESET} - Show discovered peers")
            print(f"{Colors.ORANGE}- connect{Colors.RESET} - Connect to a peer by index")
            print(f"{Colors.ORANGE}- exit{Colors.RESET} - Quit program")
            print(f"{Colors.CYAN}{'-'*30}{Colors.RESET}")

            cmd = input(f"{Colors.BOLD}> {Colors.RESET}").strip().lower()

            if cmd == "exit":
                print(f"{Colors.RED}[EXIT] Shutting down...{Colors.RESET}")
                break

            elif cmd == "discover":
                peers = user_manager.discovered
                if not peers:
                    print(f"{Colors.YELLOW}[DISCOVERY] No peers found yet.{Colors.RESET}")
                else:
                    print(f"{Colors.BROWN}[DISCOVERY] Found peers:{Colors.RESET}")
                    for i, p in enumerate(peers):
                        print(f"  [{i}] {p}")

            elif cmd == "connect":
                peers = user_manager.discovered
                if not peers:
                    print(f"{Colors.YELLOW}[CONNECT] No peers discovered.{Colors.RESET}")
                    continue

                print(f"{Colors.BROWN}Select peer index:{Colors.RESET}")
                for i, p in enumerate(peers):
                    print(f"  [{i}] {p}")
                try:
                    idx = int(input(f"{Colors.BOLD}> {Colors.RESET}"))
                    target = peers[idx]
                except (ValueError, IndexError):
                    print(f"{Colors.RED}[ERROR] Invalid index.{Colors.RESET}")
                    continue

                peer = network.connect_to_peer(target)
                if not peer:
                    print(f"{Colors.RED}[CONNECT] Failed to connect.{Colors.RESET}")
                    continue

                print(f"{Colors.BROWN}[CONNECTED] Messaging session started with {target}.{Colors.RESET}")
                print(f"{Colors.YELLOW}Type '|exit|' to leave chat{Colors.RESET}\n")

                chat_active = True

                def display_messages():
                    while running and chat_active:
                        while not peer.peer_events.messages.empty():
                            addr, message = peer.peer_events.messages.get()
                            print(f"\n{Colors.CYAN}[{bytes(addr).hex()[:6]}]:{Colors.RESET} {message['message']}")
                            print(f"{Colors.BOLD}> {Colors.RESET}", end="", flush=True)
                        time.sleep(0.1)

                msg_thread = threading.Thread(target=display_messages, daemon=True)
                msg_thread.start()

                while running:
                    msg = input(f"{Colors.BOLD}> {Colors.RESET}")
                    if msg == "|exit|":
                        print(f"{Colors.RED}[CHAT] Ending session...{Colors.RESET}")
                        chat_active = False
                        peer.disconnect()
                        break
                    elif msg.strip():
                        peer.peer_connection.send_message(msg)

            else:
                print(f"{Colors.RED}[ERROR] Unknown command.{Colors.RESET}")

    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[EXIT] Interrupted by user.{Colors.RESET}")
    finally:
        print(f"{Colors.YELLOW}[CLEANUP] Disconnecting all peers...{Colors.RESET}")
        for peer in list(network.peers.values()):
            peer.disconnect()
        discovery.stop()
        print(f"{Colors.BROWN}[EXIT] Shutdown complete.{Colors.RESET}")
