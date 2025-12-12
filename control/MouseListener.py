from abc import ABC, abstractmethod
from model.Event import Event

class MouseListener(ABC):
    @abstractmethod
    def on_mouse_event(self, event: Event) -> None:
        pass

    @abstractmethod
    def on_mouse_release(self) -> None:
        pass