import math
from numpy import ndarray
import numpy as np
from control.commands.Command import Command
from control.MouseListener import MouseListener
from model.Point import Point
from model.Color import Color
from view.Canvas import Canvas
from model.CanvasPixel import CanvasPixel 
from model.Event import Event
from control.PointTranslator import PointTranslator

class CanvasDrawCommand(Command, MouseListener):
    def __init__(self, canvas: Canvas, color: Color, position: Point, draw_size: int, line_density_factor = 0.4, max_points_for_line: int = 60, optimization_factor: float = 3, smoothing_factor: float = 0.15) -> None:
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
        self.__smooth_position = position # El punto suavizado que realmente dibuja
        self.__smoothing_factor = smoothing_factor    # Entre 0 y 1. Menos es más suave pero con más "delay"
        self.__changed_coords_set = set()
    
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

    def on_mouse_event(self, event: Event) -> None:
        target_position: Point = PointTranslator.window_to_canvas(
            event.position,
            event.layer_rotation,
            self.__canvas
        )
        new_smooth_x = self.__smooth_position.get_x() + \
                    (target_position.get_x() - self.__smooth_position.get_x()) * self.__smoothing_factor
        new_smooth_y = self.__smooth_position.get_y() + \
                    (target_position.get_y() - self.__smooth_position.get_y()) * self.__smoothing_factor
        
        new_smooth_pos = Point(int(new_smooth_x), int(new_smooth_y))
        # 3. Generar los puntos de la curva usando la posición suavizada
        __line_points = self.__line_points(new_smooth_pos)
        
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
        self.__position = new_smooth_pos
        
        self.__smooth_position = Point(new_smooth_x, new_smooth_y) # Guardar con decimales para precisión

    def on_mouse_release(self) -> None:
        image = self.__canvas.get_image()
        self.__canvas.set_image(image)

    def draw_point(self, point: Point, image: ndarray) -> None:
        canvas_w = self.__canvas.get_width()
        canvas_h = self.__canvas.get_height()
        r = self.__draw_size // 2
        px, py = point.get_x(), point.get_y()

        # 1. Definir los límites del cuadro del pincel (bounding box)
        x0, x1 = max(0, px - r), min(canvas_w, px + r + 1)
        y0, y1 = max(0, py - r), min(canvas_h, py + r + 1)

        if x0 >= x1 or y0 >= y1: return

        # 2. Crear una malla de coordenadas local para el círculo
        # Esto genera una máscara booleana circular
        yy, xx = np.ogrid[y0 - py : y1 - py, x0 - px : x1 - px]
        mask = xx**2 + yy**2 <= r**2

        # 3. Obtener el área de la imagen que vamos a afectar
        roi = image[y0:y1, x0:x1]

        # 4. Guardar píxeles para Undo (esto sigue siendo algo lento, 
        # pero solo lo hacemos para los píxeles que la máscara toca)
        # Optimización: solo guardar si el color es diferente o no está en el set
        indices_y, indices_x = np.where(mask)
        for iy, ix in zip(indices_y, indices_x):
                ay, ax = y0 + iy, x0 + ix
                if (ax, ay) not in self.__changed_coords_set:
                    # Solo guardamos lo estrictamente necesario
                    old_c = image[ay, ax].copy()
                    self.__changed_pixels.add(CanvasPixel(Point(ax, ay), Color(*old_c)))
                    self.__changed_coords_set.add((ax, ay))

        # 5. Aplicar el color de una sola vez usando la máscara
        roi[mask] = self.__color.get_list()

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

        dynamic_density = self.__line_density_factor
        if dist > self.__draw_size:
            dynamic_density *= 1.5

        # Calcular STEPS dinámicos
        STEPS = int(dist * dynamic_density)
        STEPS = max(10, min(self.__max_points_for_line, STEPS))  # clamp

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