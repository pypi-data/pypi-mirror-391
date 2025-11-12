import threading

from core.debug.debugging import log


class Listener:
    def __init__(self, event_names):
        self.lock = threading.RLock()

        self.subscriptions = {}

        for event_name in event_names:
            self.subscriptions[event_name] = []

    def subscribe(self, event_name, callback):
        with self.lock:
            if event_name not in self.subscriptions:
                log(f"event {event_name} does not exist")
                return

            log(f"subscribed to {event_name}")
            self.subscriptions[event_name].append(callback)

    def unsubscribe(self, event_name, callback=None):
        with self.lock:
            if not callback and event_name:
                self.subscriptions[event_name] = []
                log(f"cleared {event_name}")
            elif event_name and callback in self.subscriptions[event_name]:
                self.subscriptions[event_name].remove(callback)
                log(f"unsubscribed to {callback.__name__} in {event_name}")

    def emit(self, event_name, *args, **kwargs):
        with self.lock:
            callbacks = list(self.subscriptions.get(event_name, []))

        for callback in callbacks:
            callback(*args, **kwargs)
        log(f"emitted {event_name}")
