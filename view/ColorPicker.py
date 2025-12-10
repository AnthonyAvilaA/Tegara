from model.Clickeable import Clickeable
from model.Point import Point
from model.Color import Color
import numpy as np
import cv2

class ColorPicker(Clickeable):
    def __init__(self, origin: Point, width: int, height: int):
        self._origin = origin
        self._width = width
        self._height = height
        self._is_dirty = True
        self._image = np.full((height, width, 4), 0, dtype=np.uint8)
        self._image = self._generate_full_hsv()

    def get_origin_point(self) -> Point:
        return self._origin
    
    def get_width(self) -> int:
        return self._width
    
    def get_height(self) -> int:
        return self._height

    def get_image(self) -> np.ndarray:
        return self._image
    
    def is_dirty(self) -> bool:
        return self._is_dirty
    
    def clear_dirty(self) -> None:
        self._is_dirty = False
    
    def check_click(self, point: Point) -> bool:
        clicked = (self._origin.get_x() <= point.get_x() < self._origin.get_x() + self._width and
                self._origin.get_y() <= point.get_y() < self._origin.get_y() + self._height)
        return clicked
    
    def get_color_at(self, point: Point) -> Color:
        if self.check_click(point):
            local = point.substract(self._origin)
            r, g, b, a = self._image[local.get_y(), local.get_x()]
            return Color(r, g, b, a)
        else:
            return None
    
    def _generate_full_hsv(self):
        """
        Genera una paleta completa HSV:
        - Hue: horizontal (0–179)
        - Saturation: vertical (0–255)
        - Value: fijo a 255
        """
        hsv = np.zeros((self._height, self._width, 3), dtype=np.uint8)

        for y in range(self._height // 2):
            for x in range(self._width):

                # Hue → a lo largo del eje X (todo el espectro)
                h = int((x / (self._width - 1)) * 179)

                # Saturation → de gris/blanco (arriba) a color puro (abajo)
                s = int((y / (self._height // 2 - 1)) * 255)

                # Value → fijo a máximo brillo
                v = 255

                hsv[y, x] = [h, s, v]
        for y in range(self._height // 2, self._height):
            for x in range(self._width):

                # Hue → a lo largo del eje X (todo el espectro)
                h = int((x / (self._width - 1)) * 179)

                # Saturation → de color puro (arriba) a gris (abajo)
                s = int(((self._height - 1 - y) / (self._height // 2 - 1)) * 255)

                # Value → fijo a máximo brillo
                v = (255 - int(((y - self._height // 2) / (self._height // 2 - 1)) * 255))

                hsv[y, x] = [h, s, v]
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        rgba = np.dstack([rgb, np.full((self._height, self._width), 255, dtype=np.uint8)])
        return rgba