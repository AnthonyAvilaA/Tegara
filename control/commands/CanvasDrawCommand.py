import math
from numpy import ndarray
from control.Command import Command
from control.MouseListener import MouseListener
from model.Point import Point
from model.Color import Color
from view.Canvas import Canvas
from model.CanvasPixel import CanvasPixel 


class CanvasDrawCommand(Command, MouseListener):
    def __init__(self, canvas: Canvas, color: Color, position: Point, draw_size: int) -> None:
        self.canvas: Canvas = canvas
        self.color: Color = color
        self.position: Point = position
        self.prev_position: Point = position
        self.draw_size = draw_size
        self.changed_pixels: set[CanvasPixel] = set()
    
    def execute(self):
        if self.changed_pixels.__len__() > 0:
            self.redo()
        image = self.canvas.get_image()
        self.draw_point(self.position, image)
        self.canvas.set_image(image)
    
    def redo(self):
        image = self.canvas.get_image()
        for pixel in self.changed_pixels:
            x = pixel.get_x()
            y = pixel.get_y()
            image[y, x] = self.color.get_list()
        self.canvas.set_image(image)
        return

    def undo(self):
        image = self.canvas.get_image()
        for pixel in self.changed_pixels:
            x = pixel.get_x()
            y = pixel.get_y()
            image[y, x] = pixel.color.get_list()
        self.canvas.set_image(image)

    def on_mouse_event(self, event) -> None:
        new_position: Point = event.position
        line_points = self.line_points(self.prev_position, self.position, new_position)
        image = self.canvas.get_image()
        for point in line_points:
            self.draw_point(point, image)
        self.canvas.set_image(image)

        self.prev_position = self.position
        self.position = new_position

    def draw_point(self, point: Point, image: ndarray = None) -> None:
        if CanvasPixel(point, self.color) in self.changed_pixels:
            return
        for dx in range(-self.draw_size // 2 + 1, self.draw_size // 2 + 1):
            for dy in range(-self.draw_size // 2 + 1, self.draw_size // 2 + 1):
                # if dx*dx + dy*dy <= (radius*radius): para circulo perfecto
                offset = Point(dx, dy)
                new_point = point.addition(offset)
                if 0 <= new_point.get_x() < self.canvas.get_width() and 0 <= new_point.get_y() < self.canvas.get_height():
                    color = self.canvas.get_color_at(new_point)
                    if CanvasPixel(new_point, color) in self.changed_pixels:
                        continue
                    self.changed_pixels.add(CanvasPixel(new_point, color))
                    image[new_point.get_y(), new_point.get_x()] = self.color.get_list()    
        
    def line_points(self, prev_point: Point, actual_point: Point, new_point: Point) -> list[Point]:
        points = []

        x0, y0 = prev_point.get_x(), prev_point.get_y()
        x1, y1 = actual_point.get_x(), actual_point.get_y()
        x2, y2 = new_point.get_x(), new_point.get_y()

        # Pseudo punto siguiente
        x3, y3 = x2, y2

        # Distancia entre actual → new
        dist = math.hypot(x2 - x1, y2 - y1)

        # Calcular STEPS dinámicos
        MAX_STEPS = 70
        STEPS = int(dist * 0.6)
        STEPS = max(4, min(MAX_STEPS, STEPS))  # clamp

        # Catmull-Rom
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