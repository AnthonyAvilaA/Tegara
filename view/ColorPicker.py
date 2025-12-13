from view.Clickeable import Clickeable
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
        h = np.linspace(0, 179, self.__width, dtype=np.uint8)
        v = np.linspace(255, 0, self.__height, dtype=np.uint8)
        s = np.linspace(0, 255, self.__height, dtype=np.uint8)

        # Expandir dimensiones
        H = np.tile(h, (self.__height, 1))
        V = np.tile(v[:, None], (1, self.__width))
        S = np.tile(s[:, None], (1, self.__width))

        # Construir imagen HSV
        hsv = np.dstack((H, S, V))

        # Convertir a RGB y luego a RGBA
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        rgba = np.dstack([rgb, np.full_like(rgb[:, :, 0], 255)])
        return rgba