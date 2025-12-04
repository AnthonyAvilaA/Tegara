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

    def get_tuple(self) -> tuple[int, int, int]:
        return (self._r, self._g, self._b)
    
    def get_list(self) -> list[int]:
        return [self._r, self._g, self._b]

    def __eq__(self, other):
        if not isinstance(other, Color):
            return False
        return (self._r == other._r) and (self._g == other._g) and (self._b == other._b)
    
    def __hash__(self):
        return hash((self._r, self._g, self._b))

    def __repr__(self):
        return f"Color(r={self._r}, g={self._g}, b={self._b})"