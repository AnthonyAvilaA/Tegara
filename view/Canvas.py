from view.Clickeable import Clickeable
from model.ActionType import ActionType
from control.commands.Command import Command
from model.Point import Point
import numpy as np

from model.Color import Color

class Canvas(Clickeable):
    def __init__(self, width: int, height: int) -> None:
        self._image = np.full((height, width, 4), 0, dtype=np.uint8)
        self.set_dirty()
        
    def get_image(self) -> np.ndarray:
        return self._image
    
    def set_image(self, image: np.ndarray) -> None:
        self._image = image
        self.set_dirty()
        
    def is_dirty(self) -> bool:
        return self.__is_dirty
    
    def clear_dirty(self) -> None:
        self.__is_dirty = False
    
    def is_opaque(self) -> bool:
        return False

    def set_dirty(self) -> None:
        self.__is_dirty = True

    def get_color_at(self, point: Point) -> Color:
        r, g, b, a = self._image[point.get_y(), point.get_x()]
        return Color(r, g, b, a)

    def check_click(self, point: Point) -> bool:
        img_height, img_width = self._image.shape[:2]
        if 0 <= point.get_x() < img_width and 0 <= point.get_y() < img_height:
            return True
        return False
    
    def get_origin_point(self) -> Point:
        return Point(0, 0)
    
    def get_width(self) -> int:
        return self._image.shape[1]
    
    def get_height(self) -> int:
        return self._image.shape[0]