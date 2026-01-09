import easyocr
import cv2

from control.MouseListener import MouseListener
from control.commands.Command import Command
from model.ActionType import ActionType
from model.Event import Event

class CanvasTextCommand(Command, MouseListener):
    def __init__(self, main_frame_image) -> None:
        self._ocrReader = easyocr.Reader(['en'])
        self._box_starting_position = None
        self._box_ending_position = None
        self._image = main_frame_image

    def execute(self)-> None:
        print(self._box_ending_position)

    def undo(self) -> None:
        print(self._box_starting_position)

    def on_mouse_event(self, event: Event) -> None:
        if event.action_type == ActionType.LEFT_CLICK:
            self._box_starting_position = event.position
        elif event.action_type == ActionType.LEFT_DRAG and self._box_starting_position is not None:
            self._box_ending_position = event.position
            cv2.rectangle(self._image,
                          (self._box_starting_position.get_x(), self._box_starting_position.get_y()),
                          (self._box_ending_position.get_x(), self._box_ending_position.get_y()),
                          (45, 45, 45), 2)

    def on_mouse_release(self) -> None:
        if self._box_ending_position is not None:
            # RUN OCR ON THE SELECTION
            self._box_starting_position = None
            self._box_ending_position = None


    def set_image(self, image):
        self._image = image
