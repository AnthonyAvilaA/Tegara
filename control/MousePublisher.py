from control.MouseListener import MouseListener
from model.Event import Event

class MousePublisher:
    def __init__(self):
        self.subscriber: MouseListener = None
    
    def set_subscriber(self, subscriber: MouseListener) -> None:
        self.subscriber = subscriber
    
    def notify_click(self, event: Event) -> None:
        if self.subscriber:
            self.subscriber.on_mouse_event(event)
    
    def clear_subscriber(self) -> None:
        self.subscriber = None

    def has_subscriber(self) -> bool:
        return self.subscriber is not None