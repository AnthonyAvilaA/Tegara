class Color:
    def __init__(self, r: int, g: int, b: int):
        self.__r = r
        self.__g = g
        self.__b = b
    
    def get_red(self) -> int:
        return self.__r
    
    def get_green(self) -> int:
        return self.__g
    
    def get_blue(self) -> int:
        return self.__b