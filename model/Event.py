from model.Point import Point
from model.ActionType import ActionType

class Event:
    def __init__(self, position: Point, action_type: ActionType, flags: int = 0, layer_rotation: float = 0.0, windows_size = (0,0), layer_zoom_level: float = 1.0) -> None:
        self.__position = position
        self.__action_type = action_type
        self.__flags = flags
        self.__layer_rotation = layer_rotation
        self.__windows_size = windows_size
        self.__layer_zoom_level = layer_zoom_level
    
    @property
    def position(self) -> Point:
        return self.__position

    @property
    def action_type(self) -> ActionType:
        return self.__action_type
    
    @property
    def flags(self) -> int:
        return self.__flags
    
    @property
    def windows_size(self) -> tuple[int, int]:
        return self.__windows_size
    
    @property
    def layer_rotation(self) -> float:
        return self.__layer_rotation
    
    @property
    def layer_zoom_level(self) -> float:
        return self.__layer_zoom_level