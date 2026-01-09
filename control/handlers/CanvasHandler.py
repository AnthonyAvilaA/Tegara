from control.commands.CanvasTextCommand import CanvasTextCommand
from control.commands.Command import Command
from control.commands.CanvasColorPickerCommand import CanvasColorPickerCommand
from control.commands.CanvasDrawCommand import CanvasDrawCommand
from control.commands.CanvasEraseCommand import CanvasEraseCommand
from control.commands.CanvasFillCommand import CanvasFillCommand
from control.commands.CanvasEnchancedPencilCommand import CanvasEnchancedPencilCommand
from control.commands.CanvasTextDetectionComand import CanvasTxtCommand
from control.commands.ClearCanvasCommand import ClearCanvasCommand
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
                                                         self.canvas,
                                                         self.event.layer_zoom_level)

                match self.tool:
                    case Tools.PENCIL:
                        return CanvasDrawCommand(canvas=self.canvas,
                                                color=self.color,
                                                position=new_position,
                                                draw_size=self.draw_size,
                                                line_density_factor=line_density,
                                                max_points_for_line=80,
                                                optimization_factor=optimization,
                                                smoothing_factor=0.65)
                    case Tools.ERASER:
                        return CanvasEraseCommand(canvas=self.canvas,
                                                 position=new_position,
                                                    erase_size=self.draw_size,
                                                    line_density_factor=line_density,
                                                    max_points_for_line=80,
                                                    optimization_factor=optimization,
                                                    smoothing_factor=0.65)
                    case Tools.FILL:
                        return CanvasFillCommand(canvas=self.canvas,
                                                 position=new_position,
                                                 color=self.color)
                    case Tools.COLOR_PICKER:
                        return CanvasColorPickerCommand(canvas=self.canvas,
                                                        position=new_position)
                    
                    case Tools.TEXT:
                        return CanvasTxtCommand(canvas=self.canvas,
                                                color=self.color,
                                                position=new_position,
                                                draw_size=self.draw_size,
                                                line_density_factor=line_density,
                                                max_points_for_line=80,
                                                optimization_factor=optimization,
                                                smoothing_factor=0.65)
                    case Tools.ENCHANCED_PENCIL:
                        return CanvasEnchancedPencilCommand(canvas=self.canvas,
                                                color=self.color,
                                                position=new_position,
                                                draw_size=self.draw_size,
                                                line_density_factor=line_density,
                                                max_points_for_line=80,
                                                optimization_factor=optimization,
                                                smoothing_factor=0.65)
                    case Tools.CLEAR_CANVAS:
                        return ClearCanvasCommand(canvas=self.canvas)
            case _:
                return None
            