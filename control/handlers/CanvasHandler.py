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
import math

class CanvasHandler(CommandHandler):
    def __init__(self, canvas: Canvas, event: Event, color: Color, draw_size: int, tool: Tools) -> None:
        self.canvas = canvas
        self.event = event
        self.color = color
        self.draw_size = draw_size
        self.tool = tool

    def transform_point_to_canvas(self, point: Point, rotation: float, canvas_w: int, canvas_h: int, window_w: int, window_h: int) -> Point:
        cx = (window_w - canvas_w) // 2
        cy = (window_h - canvas_h) // 2

        # 1. trasladar al centro
        x = point.get_x() - cx
        y = point.get_y() - cy

        # 3. quitar rotación
        angle = -math.radians(rotation)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        rx = x * cos_a - y * sin_a
        ry = x * sin_a + y * cos_a

        # 4. volver al sistema original
        return Point(int(rx), int(ry))

    def get_command(self) -> Command:
        match self.event.action_type:
            case ActionType.LEFT_BUTTON_DOWN:
                line_density = 5 / self.draw_size
                optimization = line_density * 2

                new_position = self.transform_point_to_canvas(self.event.position,
                                                         self.event.layer_rotation,
                                                         self.canvas.get_width(),
                                                         self.canvas.get_height(),
                                                         self.event.windows_size[0],
                                                         self.event.windows_size[1])

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
            