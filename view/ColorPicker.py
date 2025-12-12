from model.Clickeable import Clickeable
from model.Point import Point
from model.Color import Color
import numpy as np
import cv2

class ColorPicker(Clickeable):
    def __init__(self, origin: Point, width: int, height: int):
        self.__origin = origin
        self.__width = width
        self.__height = height
        self.__image = np.full((height, width, 4), 0, dtype=np.uint8)
        self.__image = self._generate_full_hsv()
        self.set_dirty()

    def get_origin_point(self) -> Point:
        return self.__origin
    
    def get_width(self) -> int:
        return self.__width
    
    def get_height(self) -> int:
        return self.__height

    def get_image(self) -> np.ndarray:
        return self.__image
    
    def is_opaque(self) -> bool:
        return True
    
    def is_dirty(self) -> bool:
        return self.__is_dirty
    
    def clear_dirty(self) -> None:
        self.__is_dirty = False
    
    def set_dirty(self) -> None:
        self.__is_dirty = True
    
    def check_click(self, point: Point) -> bool:
        clicked = (self.__origin.get_x() <= point.get_x() < self.__origin.get_x() + self.__width and
                self.__origin.get_y() <= point.get_y() < self.__origin.get_y() + self.__height)
        return clicked
    
    def get_color_at(self, point: Point) -> Color:
        if self.check_click(point):
            local = point.substract(self.__origin)
            r, g, b, a = self.__image[local.get_y(), local.get_x()]
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
        hsv = np.zeros((self.__height, self.__width, 3), dtype=np.uint8)

        for y in range(self.__height * 1 // 12):
            for x in range(self.__width):

                # Hue → a lo largo del eje X (todo el espectro)
                h = int((x / (self.__width - 1)) * 179)

                # Saturation → fijo a 0 (gris/blanco)
                s = 0

                # Value → fijo a máximo brillo
                v = 255

                hsv[y, x] = [h, s, v]

        for y in range(self.__height * 1 // 12, self.__height * 6 // 12):
            for x in range(self.__width):

                # Hue → a lo largo del eje X (todo el espectro)
                h = int((x / (self.__width - 1)) * 179)

                # Saturation → de gris/blanco (arriba) a color puro (abajo)
                s = int((y / (self.__height // 2 - 1)) * 255)

                # Value → fijo a máximo brillo
                v = 255

                hsv[y, x] = [h, s, v]
        for y in range(self.__height * 6 // 12, self.__height * 11 // 12):
            for x in range(self.__width):

                # Hue → a lo largo del eje X (todo el espectro)
                h = int((x / (self.__width - 1)) * 179)

                # Saturation → de color puro (arriba) a gris (abajo)
                s = int(((self.__height - 1 - y) / (self.__height // 2 - 1)) * 255)

                # Value → fijo a máximo brillo
                v = (255 - int(((y - self.__height // 2) / (self.__height // 2 - 1)) * 255))

                hsv[y, x] = [h, s, v]
        
        for y in range(self.__height * 11 // 12, self.__height):
            for x in range(self.__width):

                # Hue → a lo largo del eje X (todo el espectro)
                h = int((x / (self.__width - 1)) * 179)

                # Saturation → fijo a 0 (gris/blanco)
                s = 0

                # Value → fijo a 0 (negro)
                v = 0

                hsv[y, x] = [h, s, v]

        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        rgba = np.dstack([rgb, np.full((self.__height, self.__width), 255, dtype=np.uint8)])
        return rgba