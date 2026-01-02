from model.Point import Point
from view.Canvas import Canvas

class PointTranslator:
    @staticmethod
    def window_to_canvas(point: Point, rotation: float, canvas: Canvas) -> Point:
        import math
        # 1. Obtener datos necesarios
        angle = -math.radians(rotation) # Inversa para "entrar" al espacio del canvas
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        origin = canvas.get_origin_point() # El centro donde se dibuja en pantalla

        # 2. Trasladar al espacio local relativo al centro (origin)
        tx = point.get_x() - origin.get_x()
        ty = point.get_y() - origin.get_y()

        # 3. Aplicar rotación inversa
        rx = tx * cos_a - ty * sin_a
        ry = tx * sin_a + ty * cos_a

        # 4. Volver a coordenadas de imagen (0,0 arriba izquierda del canvas)
        return Point(int(rx + canvas.get_width() / 2), int(ry + canvas.get_height() / 2))
    
    @staticmethod
    def canvas_to_window(point: Point, rotation: float, canvas) -> Point:
        import math
        # 1. Obtener datos necesarios
        angle = math.radians(rotation) # Rotación para "salir" del espacio del canvas
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        origin = canvas.get_origin_point() # El centro donde se dibuja en pantalla

        # 2. Trasladar al espacio local relativo al centro (origin)
        tx = point.get_x() - canvas.get_width() / 2
        ty = point.get_y() - canvas.get_height() / 2

        # 3. Aplicar rotación
        rx = tx * cos_a - ty * sin_a
        ry = tx * sin_a + ty * cos_a

        # 4. Volver a coordenadas de ventana
        return Point(int(rx + origin.get_x()), int(ry + origin.get_y()))