from control.commands.CanvasDrawCommand import CanvasDrawCommand
from control.CommandHandler import CommandHandler
from view.Canvas import Canvas
from model.Event import Event
from model.Color import Color
from model.ActionType import ActionType

class CanvasHandler(CommandHandler):
    def __init__(self, canvas: Canvas, event: Event, color: Color, draw_size: int) -> None:
        self.canvas = canvas
        self.event = event
        self.color = color
        self.draw_size = draw_size
    
    def get_command(self) -> CanvasDrawCommand:
        match self.event.action_type:
            case ActionType.LEFT_BUTTON_DOWN:
                return CanvasDrawCommand(self.canvas, self.color, self.event.position, self.draw_size)
            case _:
                return None
            