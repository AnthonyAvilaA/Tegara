class Color:
    def __init__(self, r: int, g: int, b: int):
        self._r = r
        self._g = g
        self._b = b
    
    def get_red(self) -> int:
        return self._r
    
    def get_green(self) -> int:
        return self._g
    
    def get_blue(self) -> int:
        return self._b
    
    def __eq__(self, other):
        if not isinstance(other, Color):
            return False
        return (self._r == other._r) and (self._g == other._g) and (self._b == other._b)