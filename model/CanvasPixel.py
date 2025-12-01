from model.Point import Point
from model.Color import Color

class CanvasPixel:
    def __init__(self, position: Point, color: Color) -> None:
        self.position = position
        self.color = color
    
    def __hash__(self):
        return hash((self.position.get_x(), self.position.get_y()))
