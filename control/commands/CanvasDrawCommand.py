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
        if self.changed_pixels:
            self.redo()
            return
            
        image = self.canvas.get_image()
        self.draw_point(self.position, image)
        self.canvas.set_image(image)
    
    def redo(self):
        image = self.canvas.get_image()
        color_list = self.color.get_list()
        for pixel in self.changed_pixels:
            image[pixel.get_y(), pixel.get_x()] = color_list
        self.canvas.set_image(image)
        return

    def undo(self):
        image = self.canvas.get_image()
        for pixel in self.changed_pixels:
            image[pixel.get_y(), pixel.get_x()] = pixel.color.get_list()
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

    def draw_point(self, point: Point, image: ndarray) -> None:
        canvas_width = self.canvas.get_width()
        canvas_height = self.canvas.get_height()
        target_color_list = self.color.get_list()
        radius = self.draw_size // 2
        radius_sq = radius * radius
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                
                if dx*dx + dy*dy <= radius_sq:
                    offset = Point(dx, dy)
                    new_point = point.addition(offset)
                    x, y = new_point.get_x(), new_point.get_y()
                    
                    # Comprobación de límites del canvas
                    if 0 <= x < canvas_width and 0 <= y < canvas_height:
                        candidate_pixel = CanvasPixel(new_point, Color(0, 0, 0)) 
                        
                        # 2. Si ya hemos guardado el color original de este pixel (ya está en el set), 
                        #    simplemente lo repintamos si es necesario y continuamos.
                        pixel_found = next((p for p in self.changed_pixels if p == candidate_pixel), None)
                        
                        if pixel_found:
                            image[y, x] = target_color_list
                            continue
                                                
                        original_color = self.canvas.get_color_at(new_point)
                        self.changed_pixels.add(CanvasPixel(new_point, original_color)) 
                        
                        image[y, x] = target_color_list 

    def line_points(self, prev_point: Point, actual_point: Point, new_point: Point) -> list[Point]:
        points = []

        x0, y0 = prev_point.get_x(), prev_point.get_y()
        x1, y1 = actual_point.get_x(), actual_point.get_y()
        x2, y2 = new_point.get_x(), new_point.get_y()
        x3, y3 = x2, y2

        dist = math.hypot(x2 - x1, y2 - y1)

        # Calcular STEPS dinámicos
        MAX_STEPS = 30
        STEPS = int(dist * 0.4)
        STEPS = max(4, min(MAX_STEPS, STEPS))  # clamp

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