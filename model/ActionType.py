from enum import Enum

class ActionType(Enum):
    ONE_CLICK = 1
    DOUBLE_CLICK = 2
    DRAG = 3
    UNDO = 4
    REDO = 5
    IDLE = 6
    ROTATE = 7