from model.Point import Point
from view.Canvas import Canvas
import math

class PointTranslator:
    @staticmethod
    def window_to_canvas(point: Point, rotation: float, canvas: Canvas, zoom_level: float) -> Point:
        # 1. Obtener datos necesarios
        angle = math.radians(rotation) # Inversa para "entrar" al espacio del canvas
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        origin = canvas.get_origin_point() # El centro donde se dibuja en pantalla
        cw, ch = canvas.get_width(), canvas.get_height()

        # 2. Trasladar al espacio local relativo al centro (origin)
        tx = point.get_x() - origin.get_x()
        ty = point.get_y() - origin.get_y()

        # 3. Aplicar rotación inversa
        rx = tx * cos_a - ty * sin_a
        ry = tx * sin_a + ty * cos_a

        rx /= zoom_level
        ry /= zoom_level

        # 4. Volver a coordenadas de imagen (0,0 arriba izquierda del canvas)
        return Point(int(rx + canvas.get_width() / 2), int(ry + canvas.get_height() / 2))