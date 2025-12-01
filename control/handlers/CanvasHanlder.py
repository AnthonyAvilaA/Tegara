from control.commands.CanvasDrawCommand import CanvasDrawCommand
from control.CommandHandler import CommandHandler
from model.Event import Event
from model.Color import Color
from model.ActionType import ActionType
from numpy import ndarray
from cv2 import RGB

class CanvasHandler(CommandHandler):
    def __init__(self, canvas: ndarray, event: Event, color: Color) -> None:
        self.canvas = canvas
    
    def get_command(self) -> CanvasDrawCommand:
        if self.event.action_type == ActionType.BUTTON_PRESS:
            return CanvasDrawCommand(
                self.canvas,