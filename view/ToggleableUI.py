from model.Clickeable import Clickeable
from typing import Generic, TypeVar
from model.Point import Point
import numpy as np

T = TypeVar("T", bound=Clickeable)

class ToggleableUI(Generic[T], Clickeable):
    def __init__(self, point: Point, width: int, height: int, image: np.ndarray, element: T, toggled_on: bool = False) -> None:
        self.element: T = element
        self._point = point
        self._width = width
        self._height = height
        self._image = image
        self.toggled_on = toggled_on

    def toggle(self) -> None:
        self.toggled_on = not self.toggled_on
    
    def set_toggle(self, state: bool) -> None:
        self.toggled_on = state

    def get_image(self) -> np.ndarray:
        if self.toggled_on:
            return self.element.get_image()
        else:
            return self._image
    
    def set_image(self, image: np.ndarray) -> None:
        self._image = image

    def check_click(self, point: Point) -> bool:
        if self.toggled_on:
            return self.element.check_click(point)
        else:
            clicked = (self._point.get_x() <= point.get_x() < self._point.get_x() + self._width and
                self._point.get_y() <= point.get_y() < self._point.get_y() + self._height)
            return clicked

    def get_origin_point(self) -> Point:
        if self.toggled_on:
            return self.element.get_origin_point()
        else:
            return self._point

    def get_width(self) -> int:
        if self.toggled_on:
            return self.element.get_width()
        else:
            return self._width

    def get_height(self) -> int:
        if self.toggled_on:
            return self.element.get_height()
        else:
            return self._height
    
    def get_element(self) -> T:
        return self.element
    
    def is_toggled_on(self) -> bool:
        return self.toggled_on