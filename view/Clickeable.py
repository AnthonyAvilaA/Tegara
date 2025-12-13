from abc import abstractmethod
from model.Point import Point
from view.Drawable import Drawable

class Clickeable(Drawable):
    @abstractmethod
    def is_dirty(self) -> bool:
        pass
    
    @abstractmethod
    def clear_dirty(self) -> None:
        pass

    @abstractmethod
    def set_dirty(self) -> None:
        pass
    
    @abstractmethod
    def check_click(self, point: Point) -> bool:
        pass