from abc import ABC, abstractmethod
from model.Event import Event
from control.commands.Command import Command

class CommandHandler(ABC):
    @abstractmethod
    def get_command(self) -> Command:
        pass