from control.commands.CanvasDrawCommand import CanvasDrawCommand
from control.commands.CanvasEraseCommand import CanvasEraseCommand
from control.handlers.CommandHandler import CommandHandler
from view.Canvas import Canvas
from model.Event import Event
from model.Color import Color
from model.ActionType import ActionType
from definitions.Tools import Tools

class CanvasHandler(CommandHandler):
    def __init__(self, canvas: Canvas, event: Event, color: Color, draw_size: int, tool: Tools) -> None:
        self.canvas = canvas
        self.event = event
        self.color = color
        self.draw_size = draw_size
        self.tool = tool
    
    def get_command(self) -> CanvasDrawCommand:
        match self.event.action_type:
            case ActionType.LEFT_BUTTON_DOWN:
                line_density = 3 / self.draw_size
                optimization = line_density * 2
                match self.tool:
                    case Tools.PENCIL:
                        print("Creating CanvasDrawCommand")
                        return CanvasDrawCommand(canvas=self.canvas,
                                                color=self.color,
                                                position=self.event.position,
                                                draw_size=self.draw_size,
                                                line_density_factor=line_density,
                                                max_points_for_line=80,
                                                optimization_factor=optimization)
                    case Tools.ERASER:
                        print("Creating CanvasEraseCommand")
                        return CanvasEraseCommand(canvas=self.canvas,
                                                 position=self.event.position,
                                                    erase_size=self.draw_size,
                                                    line_density_factor=line_density,
                                                    max_points_for_line=80,
                                                    optimization_factor=optimization)

            case _:
                return None
            