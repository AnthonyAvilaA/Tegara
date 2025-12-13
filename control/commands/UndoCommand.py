from control.commands.Command import Command

class UndoCommand(Command):
    def __init__(self, undo_history, redo_history):
        self.undo_history = undo_history
        self.redo_history = redo_history

    def execute(self):
        if self.undo_history:
            last_command = self.undo_history.pop()
            self.redo_history.append(last_command)
            last_command.undo()

    def undo(self):
        pass
