from view.Clickeable import Clickeable
from typing import Generic, TypeVar
from model.Point import Point
import numpy as np

T = TypeVar("T", bound=Clickeable)

class ToggleableUI(Generic[T], Clickeable):
    def __init__(self, point: Point, width: int, height: int, image: np.ndarray, element: T, toggled_on: bool = False) -> None:
        self.element: T = element
        self.__point = point
        self.__width = width
        self.__height = height
        self.__image = image
        self.__toggled_on = toggled_on
        self.set_dirty()

    def toggle(self) -> None:
        self.__toggled_on = not self.__toggled_on
        self.set_dirty()
    
    def set_toggle(self, state: bool) -> None:
        self.__toggled_on = state
        self.set_dirty()

    def get_image(self) -> np.ndarray:
        if self.__toggled_on:
            return self.element.get_image()
        else:
            return self.__image
    
    def set_image(self, image: np.ndarray) -> None:
        self.__image = image
        self.set_dirty()
    
    def is_dirty(self) -> bool:
        if self.__toggled_on:
            return self.element.is_dirty()
        else:
            return self.__is_dirty
    
    def clear_dirty(self) -> None:
        if self.__toggled_on:
            self.element.clear_dirty()
        else:
            self.__is_dirty = False

    def set_dirty(self) -> None:
        if self.__toggled_on:
            self.element.set_dirty()
        else:
            self.__is_dirty = True

    def check_click(self, point: Point) -> bool:
        if self.__toggled_on:
            return self.element.check_click(point)
        else:
            clicked = (self.__point.get_x() <= point.get_x() < self.__point.get_x() + self.__width and
                self.__point.get_y() <= point.get_y() < self.__point.get_y() + self.__height)
            return clicked

    def get_origin_point(self) -> Point:
        if self.__toggled_on:
            return self.element.get_origin_point()
        else:
            return self.__point

    def get_width(self) -> int:
        if self.__toggled_on:
            return self.element.get_width()
        else:
            return self.__width

    def get_height(self) -> int:
        if self.__toggled_on:
            return self.element.get_height()
        else:
            return self.__height
    
    def get_element(self) -> T:
        return self.element
    
    def is_toggled_on(self) -> bool:
        return self.__toggled_on
    
    def is_opaque(self) -> bool:
        if self.__toggled_on:
            return self.element.is_opaque()
        else:
            raise RuntimeError("This method should be overridden")