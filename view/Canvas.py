from model.Clickeable import Clickeable
from model.ActionType import ActionType
from control.Command import Command
import numpy as np

from model.Color import Color

class Canvas(Clickeable):
    def __init__(self, width: int, height: int) -> None:
        self._image = np.array([[255, 255, 255] * width] * height, dtype=np.uint8)
        self._image = np.full((height, width, 3), 255, dtype=np.uint8)

    def get_image(self):
        return self._image.copy()
    
    def set_image(self, image: np.ndarray) -> None:
        self._image = image

    def get_color_at(self, x: int, y: int) -> Color:
        return Color(*self._image[y, x])

    def check_click(self, x: int, y: int) -> bool:
        img_height, img_width = self._image.shape[:2]
        if 0 <= x < img_width and 0 <= y < img_height:
            return True
        return False
    
    def get_width(self) -> int:
        return self._image.shape[1]
    
    def get_height(self) -> int:
        return self._image.shape[0]