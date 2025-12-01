from model.Clickeable import Clickeable
from model.ActionType import ActionType
from control.Command import Command
import numpy as np

class Canvas(Clickeable):
    def __init__(self, width: int, height: int) -> None:
        self._image = np.array([[255, 255, 255] * width] * height, dtype=np.uint8)

    @property
    def __image(self):
        return self._image

    @__image.setter
    def __image(self, value):
        self._image = value

    def check_click(self, x: int, y: int) -> bool:
        img_height, img_width = self._image.shape[:2]
        center_x, center_y = self._center
        if (center_x - img_width // 2 <= x <= center_x + img_width // 2 and
                center_y - img_height // 2 <= y <= center_y + img_height // 2):
            return True
        return False

    def create_command(self, action_type: ActionType) -> Command:
        return Command(action_type, self)

    def get_image(self):
        return self.__image