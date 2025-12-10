from abc import ABC, abstractmethod
from model.Point import Point

class Clickeable(ABC):
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
    def get_image(self):
        pass
    
    @abstractmethod
    def check_click(self, point: Point) -> bool:
        pass
