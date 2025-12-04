from model.Clickeable import Clickeable
from model.Point import Point
from model.Color import Color
import numpy as np
import cv2

class ColorPicker(Clickeable):
    def __init__(self, x: int, y: int, width: int, height: int):
        self._origin = Point(x, y)
        self._width = width
        self._height = height
        self._image = np.full((height, width, 3), 0, dtype=np.uint8)
        self._image = self._generate_full_hsv()

    def get_x(self) -> int:
        return self._origin.get_x()
    
    def get_y(self) -> int:
        return self._origin.get_y()
    
    def get_width(self) -> int:
        return self._width
    
    def get_height(self) -> int:
        return self._height

    def get_image(self) -> np.ndarray:
        return self._image
    
    def check_click(self, x: int, y: int) -> bool:
        return (self._origin.get_x() <= x <= self._origin.get_x() + self._width and
                self._origin.get_y() <= y <= self._origin.get_y() + self._height)
    
    def get_color_at(self, x: int, y: int) -> Color:
        if self.check_click(x, y):
            local_x = x - self._origin.get_x()
            local_y = y - self._origin.get_y()
            r, g, b = self._image[local_y, local_x]
            return Color(r, g, b)
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
        return rgb