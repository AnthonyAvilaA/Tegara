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
        for i in range(height):
            for j in range(width):
                r = int((j / width) * 255)
                g = int((i / height) * 255)
                b = 255 - r
                self._image[i, j] = [r, g, b]

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