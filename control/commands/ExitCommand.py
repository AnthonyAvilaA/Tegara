from control.Command import Command
import cv2

class ExitCommand(Command):
    def __init__(self):
        pass

    def execute(self):
        cv2.destroyAllWindows()
        exit(0)

    def undo(self):
        pass