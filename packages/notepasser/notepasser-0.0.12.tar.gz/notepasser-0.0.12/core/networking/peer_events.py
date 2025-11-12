import json
import queue

from core.debug.debugging import log


class PeerEvents:
    def __init__(self, disconnect, listener, peer_state):
        self.disconnect = disconnect
        self.listener = listener

        self.peer_state = peer_state

        self.messages = queue.Queue()
        self.token_requests = queue.Queue()

    def on_event_received(self, event):
        peer_verify_key = self.peer_state.peer_information.get("verify_key")
        my_verify_key = self.peer_state.my_information.get("verify_key")

        if not event or not "type" in event:
            log(f"[{peer_verify_key}] event missing type! {json.dumps(event)}")
            return

        match event["type"]:
            case "message_received":
                self.messages.put([peer_verify_key, event])
                self.listener.emit("message_received", [peer_verify_key, event])
            case "message_sent":
                self.messages.put([my_verify_key, event])
                self.listener.emit("message_sent", [my_verify_key, event])
            case "trusted_token":
                self.token_requests.put([peer_verify_key, event])
            case "disconnect":
                self.disconnect("disconnect gracefully")
                return
            case _:
                self.disconnect("message type not matched")
