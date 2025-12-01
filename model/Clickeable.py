from abc import ABC, abstractmethod
from control.Command import Command
from model.ActionType import ActionType

class Clickeable(ABC):
    @property
    @abstractmethod
    def __center(self):
        pass
    
    @property
    @abstractmethod
    def __image(self):
        pass
    
    
    @abstractmethod
    def check_click(self, x: int, y: int) -> bool:
        pass
    
    @abstractmethod
    def create_command(self, action_type: ActionType) -> Command:
        pass
    
    @abstractmethod
    def get_image(self):
        pass
