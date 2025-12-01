from control.Command import Command
from control.MouseListener import MouseListener
from model.Point import Point
from model.Color import Color
from view.Canvas import Canvas
from model.CanvasPixel import CanvasPixel 


class CanvasDrawCommand(Command, MouseListener):
    def __init__(self, canvas: Canvas, color: Color, x, y) -> None:
        self.canvas: Canvas = canvas
        self.color: Color = color
        self.position: Point = Point(x, y)
        self.changed_pixels: set[CanvasPixel] = set()
    
    def execute(self):
        canva_color = self.canvas.get_color_at(self.position.get_x(), self.position.get_y())
        self.change_image(self.position, self.color)
        self.add_changed_pixel(self.position, canva_color)
        
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
        for point in line_points:
            if self.changed_pixels.__contains__(CanvasPixel(point, self.color)):
                continue
            canva_color = self.canvas.get_color_at(point.get_x(), point.get_y())
            if canva_color == self.color:
                continue
            self.add_changed_pixel(point, canva_color)
            self.change_image(point, self.color)
        self.position = Point(x, y)

    def add_changed_pixel(self, point: Point, color: Color):
        self.changed_pixels.add(CanvasPixel(point, color))
    
    def change_image(self, point: Point, color: Color):
        image = self.canvas.get_image()
        image[point.get_y(), point.get_x()] = [color.get_red(), color.get_green(), color.get_blue()]
        self.canvas.set_image(image)
    
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