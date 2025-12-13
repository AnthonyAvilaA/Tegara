from abc import ABC, abstractmethod
from model.Point import Point
from numpy import ndarray

class Drawable(ABC):
    @abstractmethod
    def get_origin_point() -> Point:
        pass
    
    @abstractmethod
    def get_width() -> int:
        pass
    
    @abstractmethod
    def get_height() -> int:
        pass

    @abstractmethod
    def is_opaque() -> bool:
        pass

    @abstractmethod
    def get_image() -> ndarray:
        pass