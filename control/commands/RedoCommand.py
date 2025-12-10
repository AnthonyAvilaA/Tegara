from control.Command import Command

class RedoCommand(Command):
    def __init__(self, redo_history, undo_history):
        self.redo_history = redo_history
        self.undo_history = undo_history

    def execute(self):
        if self.redo_history:
            last_command = self.redo_history.pop()
            self.undo_history.append(last_command)
            last_command.execute()

    def undo(self):
        pass
