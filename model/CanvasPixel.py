from model.Point import Point

class CanvasPixel:
    def __init__(self, point: Point, color) -> None:
        self.point = point
        self.color = color