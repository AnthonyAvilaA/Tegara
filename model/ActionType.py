from enum import Enum

class ActionType(Enum):
    LEFT_CLICK = 1
    RIGHT_CLICK = 2
    LEFT_BUTTON_DOWN = 3
    LEFT_BUTTON_UP = 4
    RIGHT_BUTTON_DOWN = 5
    RIGHT_BUTTON_UP = 6
    LEFT_DRAG = 7
    RIGHT_DRAG = 8
    SCROLL = 9