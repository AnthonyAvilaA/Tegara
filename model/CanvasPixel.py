from model.Point import Point
from model.Color import Color

class CanvasPixel(Point):
    def __init__(self, position: Point, color: Color) -> None:
        super().__init__(position.get_x(), position.get_y())
        self.color = color

    def __eq__(self, other):
        if not isinstance(other, CanvasPixel):
            return False
        return (self.get_x() == other.get_x()) and (self.get_y() == other.get_y())
    
    def __hash__(self):
        return hash((self.get_x(), self.get_y()))
    
    def __repr__(self):
        return f"CanvasPixel(x={self.get_x()}, y={self.get_y()}, color={self.color})"
