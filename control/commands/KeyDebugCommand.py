from control.commands.Command import Command
from definitions.Key import Key


class KeyDebugCommand(Command):
    def __init__(self, key: Key):
        self.key_pressed = key

    def execute(self):
        print(f"Key pressed: {self.key_pressed} {chr(self.key_pressed)}")

    def undo(self):
        pass

