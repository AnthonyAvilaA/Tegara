from control.commands.Command import Command
from control.commands.CanvasColorPickerCommand import CanvasColorPickerCommand
from control.commands.CanvasDrawCommand import CanvasDrawCommand
from control.commands.CanvasEraseCommand import CanvasEraseCommand
from control.commands.CanvasFillCommand import CanvasFillCommand
from control.handlers.CommandHandler import CommandHandler
from model.Point import Point
from view.Canvas import Canvas
from model.Event import Event
from model.Color import Color
from model.ActionType import ActionType
from definitions.Tools import Tools
from control.PointTranslator import PointTranslator
import math

class CanvasHandler(CommandHandler):
    def __init__(self, canvas: Canvas, event: Event, color: Color, draw_size: int, tool: Tools) -> None:
        self.canvas = canvas
        self.event = event
        self.color = color
        self.draw_size = draw_size
        self.tool = tool
    
    def get_command(self) -> Command:
        match self.event.action_type:
            case ActionType.LEFT_BUTTON_DOWN:
                line_density = 5 / self.draw_size
                optimization = line_density * 2

                new_position = PointTranslator.window_to_canvas(self.event.position,
                                                         self.event.layer_rotation,
                                                         self.canvas)

                match self.tool:
                    case Tools.PENCIL:
                        return CanvasDrawCommand(canvas=self.canvas,
                                                color=self.color,
                                                position=new_position,
                                                draw_size=self.draw_size,
                                                line_density_factor=line_density,
                                                max_points_for_line=80,
                                                optimization_factor=optimization)
                    case Tools.ERASER:
                        return CanvasEraseCommand(canvas=self.canvas,
                                                 position=new_position,
                                                    erase_size=self.draw_size,
                                                    line_density_factor=line_density,
                                                    max_points_for_line=80,
                                                    optimization_factor=optimization)
                    case Tools.FILL:
                        return CanvasFillCommand(canvas=self.canvas,
                                                 position=new_position,
                                                 color=self.color)
                    case Tools.COLOR_PICKER:
                        return CanvasColorPickerCommand(canvas=self.canvas,
                                                        position=new_position)

            case _:
                return None
            