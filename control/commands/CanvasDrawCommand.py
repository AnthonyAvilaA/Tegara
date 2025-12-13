import math
from numpy import ndarray
from control.commands.Command import Command
from control.MouseListener import MouseListener
from model.Point import Point
from model.Color import Color
from view.Canvas import Canvas
from model.CanvasPixel import CanvasPixel 


class CanvasDrawCommand(Command, MouseListener):
    def __init__(self, canvas: Canvas, color: Color, position: Point, draw_size: int, line_density_factor = 0.4, max_points_for_line: int = 60, optimization_factor: float = 3) -> None:
        self.__canvas: Canvas = canvas
        self.__color: Color = color
        self.__position: Point = position
        self.__prev_position: list[Point] = [position]
        self.__draw_size = draw_size
        self.__changed_pixels: set[CanvasPixel] = set()
        self.__points_since_last_update = 0
        self.__optimization_factor = optimization_factor
        self.__max_points_for_line = max_points_for_line
        self.__line_density_factor = line_density_factor
    
    def execute(self):
        if self.__changed_pixels:
            self.redo()
            return
            
        image = self.__canvas.get_image()
        self.draw_point(self.__position, image)
        self.__canvas.set_image(image)
    
    def redo(self):
        image = self.__canvas.get_image()
        color_list = self.__color.get_list()
        for pixel in self.__changed_pixels:
            image[pixel.get_y(), pixel.get_x()] = color_list
        self.__canvas.set_image(image)
        return

    def undo(self):
        image = self.__canvas.get_image()
        for pixel in self.__changed_pixels:
            image[pixel.get_y(), pixel.get_x()] = pixel.color.get_list()
        self.__canvas.set_image(image)

    def on_mouse_event(self, event) -> None:
        new_position: Point = event.position
        __line_points = self.__line_points(new_position)
        image = self.__canvas.get_image()

        for point in __line_points:
            self.draw_point(point, image)
            self.__points_since_last_update += 1
        
        if self.__points_since_last_update > self.__draw_size * self.__optimization_factor:
            self.__canvas.set_image(image)
            self.__points_since_last_update = 0

        self.__prev_position.append(self.__position)
        if len(self.__prev_position) > 5:
            self.__prev_position.pop(0)
        self.__position = new_position

    def on_mouse_release(self) -> None:
        image = self.__canvas.get_image()
        self.__canvas.set_image(image)

    def draw_point(self, point: Point, image: ndarray) -> None:
        canvas_width = self.__canvas.get_width()
        canvas_height = self.__canvas.get_height()
        target_color_list = self.__color.get_list()
        radius = self.__draw_size // 2
        radius_sq = radius * radius
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                
                if dx*dx + dy*dy <= radius_sq:
                    offset = Point(dx, dy)
                    new_point = point.addition(offset)
                    x, y = new_point.get_x(), new_point.get_y()
                    
                    if self.__is_point_in_canvas(new_point):
                        continue
                    
                    if 0 <= x < canvas_width and 0 <= y < canvas_height:    
                        original_color = self.__canvas.get_color_at(new_point)
                        self.__changed_pixels.add(CanvasPixel(new_point, original_color)) 
                        image[y, x] = target_color_list

    def __is_point_in_canvas(self, point: Point) -> bool:
        return CanvasPixel(point, self.__color) in self.__changed_pixels                        

    def __line_points(self, new_position: Point) -> list[Point]:
        points = []

        p0 = self.__prev_position[-2] if len(self.__prev_position) >= 2 else self.__prev_position[-1]
        p1 = self.__prev_position[-1]
        p2 = self.__position
        p3 = new_position

        x0, y0 = p0.get_x(), p0.get_y()
        x1, y1 = p1.get_x(), p1.get_y()
        x2, y2 = p2.get_x(), p2.get_y()
        x3, y3 = p3.get_x(), p3.get_y()


        dist = math.hypot(x2 - x1, y2 - y1)

        # Calcular STEPS dinámicos
        STEPS = int(dist * self.__line_density_factor)
        STEPS = max(4, min(self.__max_points_for_line, STEPS))  # clamp

        for i in range(STEPS + 1):
            t = i / STEPS
            tt = t * t
            ttt = tt * t
            
            px = 0.5 * (
                (2 * x1) +
                (-x0 + x2) * t +
                (2*x0 - 5*x1 + 4*x2 - x3) * tt +
                (-x0 + 3*x1 - 3*x2 + x3) * ttt
            )

            py = 0.5 * (
                (2 * y1) +
                (-y0 + y2) * t +
                (2*y0 - 5*y1 + 4*y2 - y3) * tt +
                (-y0 + 3*y1 - 3*y2 + y3) * ttt
            )

            points.append(Point(int(px), int(py)))

        return points