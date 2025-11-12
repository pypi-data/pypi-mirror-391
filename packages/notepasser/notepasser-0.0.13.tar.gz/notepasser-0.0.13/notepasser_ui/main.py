import sys
import threading
import time

from PySide6.QtWidgets import QApplication

from core.node import Node
from notepasser_ui.chat import ChatWindow


class GuiNode(Node):
    def __init__(self, get_trusted_token_input):
        super().__init__(get_trusted_token_input)

        self.app = QApplication(sys.argv)

        self.chat_window = ChatWindow(self)
        self.chat_window.show()
        self.chat_window.user_selected_signal.connect(self.chat_selected)
        self.chat_window.send_message_signal.connect(self.send_message)
        self.chat_window.window_closed_signal.connect(self.disconnect)

        self.cur_peer = None

        self.app.exec()

    def chat_selected(self, user_verify_key):
        user_verify_key = bytes.fromhex(user_verify_key)
        self.cur_peer = self.network_manager.connect_to_peer(user_verify_key)

        if not self.cur_peer: return

        queued_messages = []
        messages_lock = threading.Lock()

        def display_messages():
            nonlocal queued_messages
            while True:
                while not self.cur_peer.peer_events.messages.empty():
                    verify_key, payload = self.cur_peer.peer_events.messages.get()
                    with messages_lock:
                        queued_messages.append(f"[{bytes(verify_key).hex()[:6]}] {payload['message']}")
                time.sleep(0.1)

        msg_thread = threading.Thread(target=display_messages, daemon=True)
        msg_thread.start()

        self.chat_window.load_chat(queued_messages)

        self.cur_peer.listener.subscribe("message_received", self.handle_message_received)
        self.cur_peer.listener.subscribe("message_sent", self.handle_message_received)

    def handle_message_received(self, payload):
        self.chat_window.add_message_to_chat(f"[{bytes(payload[0]).hex()[:6]}] {payload[1]['message']}")

    def send_message(self, message_content):
        if not self.cur_peer: return
        self.cur_peer.peer_connection.send_message(message_content)

    def disconnect(self):
        if not self.cur_peer: return
        self.cur_peer.disconnect()


def main():
    GuiNode(input)

if __name__ == '__main__':
    main()
