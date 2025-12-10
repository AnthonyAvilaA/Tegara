class Point:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y
    
    def get_x(self) -> int:
        return self._x
    
    def get_y(self) -> int:
        return self._y
    
    def scale_axes(self, scale_x: float, scale_y: float) -> "Point":
        scaled_x = self._x * scale_x
        scaled_y = self._y * scale_y
        return Point(scaled_x, scaled_y)
    
    def lerp(self, other: "Point", t: float) -> "Point":
        x = self._x + (other.get_x() - self._x) * t
        y = self._y + (other.get_y() - self._y) * t
        return Point(x, y)

    def scale(self, factor: float) -> "Point":
        x = self._x * factor
        y = self._y * factor
        return Point(x, y)
    
    def substract(self, other: "Point") -> "Point":
        x = self._x - other.get_x()
        y = self._y - other.get_y()
        return Point(x, y)
    
    def addition(self, other: "Point") -> "Point":
        x = self._x + other.get_x()
        y = self._y + other.get_y()
        return Point(x, y)
    
    def to_int(self) -> "Point":
        return Point(int(self._x), int(self._y))
    
    def __repr__(self):
        return f"Point(x={self._x}, y={self._y})"