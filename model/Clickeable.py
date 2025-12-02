from abc import ABC, abstractmethod
from control.Command import Command
from model.ActionType import ActionType

class Clickeable(ABC):
    @abstractmethod
    def get_x() -> int:
        pass

    @abstractmethod
    def get_y() -> int:
        pass
    
    @abstractmethod
    def get_width() -> int:
        pass
    
    @abstractmethod
    def get_height() -> int:
        pass

    @abstractmethod
    def get_image(self):
        pass
    
    @abstractmethod
    def check_click(self, x: int, y: int) -> bool:
        pass
