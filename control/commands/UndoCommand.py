from control.Command import Command

class UndoCommand(Command):
    def __init__(self, command_history):
        self.command_history = command_history

    def execute(self):
        print("Undo")
        if self.command_history:
            last_command = self.command_history.pop()
            last_command.undo()

    def undo(self):
        pass
