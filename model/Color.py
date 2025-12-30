class Color:
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        self._r = int(r)
        self._g = int(g)
        self._b = int(b)
        self._a = int(a)
    
    def get_red(self) -> int:
        return self._r
    
    def get_green(self) -> int:
        return self._g
    
    def get_blue(self) -> int:
        return self._b

    def get_alpha(self) -> int:
        return self._a

    def get_tuple(self) -> tuple[int, int, int, int]:
        return (self._r, self._g, self._b, self._a)
    
    def get_list(self) -> list[int]:
        return [self._r, self._g, self._b, self._a]

    def __eq__(self, other):
        if not isinstance(other, Color):
            return False
        return (self._r == other._r) and (self._g == other._g) and (self._b == other._b) and (self._a == other._a)
    
    def __hash__(self):
        return hash((self._r, self._g, self._b, self._a))

    def __repr__(self):
        return f"Color(r={self._r}, g={self._g}, b={self._b}, a={self._a})"



COLOR_DEFAULT_COLOR = Color(13, 13, 13)
COLOR_BLACK = Color(0, 0, 0)
COLOR_WHITE = Color(255, 255, 255)
COLOR_BLUE = Color(0, 0, 255)
COLOR_RED = Color(255, 0, 0)
COLOR_GREEN = Color(0, 255, 0)
COLOR_TRANSPARENT = Color(0, 0, 0, 0)