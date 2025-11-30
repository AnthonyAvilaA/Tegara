class Point:
    def __init__(self, x: int, y: int):
        self.__x = x
        self.__y = y
    
    def get_x(self) -> int:
        return self.__x
    
    def get_y(self) -> int:
        return self.__y