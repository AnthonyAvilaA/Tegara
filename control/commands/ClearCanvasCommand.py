from view.Canvas import Canvas
from control.commands.Command import Command

class ClearCanvasCommand(Command):
    def __init__(self, canvas: Canvas, color=(255, 255, 255, 255)):
        self.canvas = canvas
        self.color = color
        self._backup = None

    def execute(self):
        # guardar copia para undo
        self._backup = self.canvas.get_image().copy()

        # limpiar canvas
        print("Clearing canvas...")
        self.canvas.clear(self.color)
        self.canvas.set_dirty()

    def undo(self):
        if self._backup is not None:
            self.canvas.set_image(self._backup)
            self.canvas.set_dirty()
