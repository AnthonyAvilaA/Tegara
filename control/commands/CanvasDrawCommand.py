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
        self.draw_size = draw_size
        self.changed_pixels: set[CanvasPixel] = set()
    
    def execute(self):
        image = self.canvas.get_image()
        self.draw_point(self.position, image)
        self.canvas.set_image(image)
        
    def undo(self):
        image = self.canvas.get_image()
        for pixel in self.changed_pixels:
            x = pixel.position.get_x()
            y = pixel.position.get_y()
            color = pixel.color
            image[y, x] = [color.get_red(), color.get_green(), color.get_blue()]
        self.canvas.set_image(image)

    def on_mouse_event(self, event) -> None:
        x = event.position.get_x()
        y = event.position.get_y()
        line_points = self.line_points(self.position.get_x(), self.position.get_y(), x, y)
        image = self.canvas.get_image()
        for point in line_points:
            self.draw_point(point, image)
        self.canvas.set_image(image)
        self.position = Point(x, y)

    def draw_point(self, point: Point, image: ndarray = None) -> None:
        if CanvasPixel(point, self.color) in self.changed_pixels:
            return
        for dx in range(-self.draw_size // 2 + 1, self.draw_size // 2 + 1):
            for dy in range(-self.draw_size // 2 + 1, self.draw_size // 2 + 1):
                # if dx*dx + dy*dy <= (radius*radius): para circulo perfecto
                px = point.get_x() + dx
                py = point.get_y() + dy
                if 0 <= px < self.canvas.get_width() and 0 <= py < self.canvas.get_height():
                    color = self.canvas.get_color_at(px, py)
                    if CanvasPixel(Point(px, py), color) in self.changed_pixels:
                        continue
                    self.changed_pixels.add(CanvasPixel(Point(px, py), color))
                    image[py, px] = self.color.get_list()    
    
    def line_points(self, x1: int, y1: int, x2: int, y2: int) -> list[Point]:
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            points.append(Point(x1, y1))
            if x1 == x2 and y1 == y2:
                break
            err2 = err * 2
            if err2 > -dy:
                err -= dy
                x1 += sx
            if err2 < dx:
                err += dx
                y1 += sy
        return points