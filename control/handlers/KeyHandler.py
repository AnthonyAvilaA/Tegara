from control.Command import Command
from control.commands.KeyDebugCommand import KeyDebugCommand
from definitions.key import Key

class KeyHandler:
    def __init__(self):
        self.commands = dict()

    def add_command_for_key(self, command: Command, key: Key) -> None:
        self.commands[key] = command

    def get_command(self, key) -> Command:
        return self.commands.get(key, KeyDebugCommand(key))