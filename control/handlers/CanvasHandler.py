from control.commands.CanvasDrawCommand import CanvasDrawCommand
from control.CommandHandler import CommandHandler
from model.Canvas import Canvas
from model.Event import Event
from model.Color import Color
from model.ActionType import ActionType

class CanvasHandler(CommandHandler):
    def __init__(self, canvas: Canvas, event: Event, color: Color) -> None:
        self.canvas = canvas
        self.event = event
        self.color = color
    
    def get_command(self) -> CanvasDrawCommand:
        match self.event.action_type:
            case ActionType.LEFT_BUTTON_DOWN:
                return CanvasDrawCommand(self.canvas, self.color, self.event.position.get_x(), self.event.position.get_y())
            case _:
                return None
            