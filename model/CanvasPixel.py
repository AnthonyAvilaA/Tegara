from model.Point import Point
from model.Color import Color

class CanvasPixel:
    def __init__(self, position: Point, color: Color) -> None:
        self.position = position
        self.color = color

    def __eq__(self, other):
        if not isinstance(other, CanvasPixel):
            return False
        return (self.position.get_x() == other.position.get_x()) and (self.position.get_y() == other.position.get_y())
    
    def __hash__(self):
        return hash((self.position.get_x(), self.position.get_y()))
