from control.commands.Command import Command
from control.commands.KeyDebugCommand import KeyDebugCommand
from definitions.key import Key
from control.handlers.CommandHandler import CommandHandler

class KeyHandler(CommandHandler):
    def __init__(self):
        self.commands = dict()

    def add_command_for_key(self, command: Command, *key_list: Key) -> None:
        for key in key_list:
            self.commands[key] = command

    def get_command(self, key) -> Command:
        return self.commands.get(key, KeyDebugCommand(key))
