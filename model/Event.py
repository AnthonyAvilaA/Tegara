from model.Point import Point
from model.ActionType import ActionType

class Event:
    def __init__(self, position: Point, action_type: ActionType):
        self.__position = position
        self.__action_type = action_type

    @property
    def position(self) -> Point:
        return self.__position

    @property
    def action_type(self) -> ActionType:
        return self.__action_type