from model.Point import Point
from model.ActionType import ActionType

class Event:
    def __init__(self, position: Point, action_type: ActionType, flags: int = 0) -> None:
        self.__position = position
        self.__action_type = action_type
        self.__flags = flags

    @property
    def position(self) -> Point:
        return self.__position

    @property
    def action_type(self) -> ActionType:
        return self.__action_type
    
    @property
    def flags(self) -> int:
        return self.__flags