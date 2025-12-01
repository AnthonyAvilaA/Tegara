from control.Command import Command
from control.MouseListener import MouseListener
from model.Event import Event
from model.Point import Point
from model.CanvasPixel import CanvasPixel 


class CanvasDrawCommand(Command, MouseListener):
    def __init__(self, canvas, color) -> None:
        self.canvas = canvas
        self.color = color
        self.changed_pixels = []
    
    def execute(self):
        self.draw_function(self.canvas, *self.args, **self.kwargs)

    def undo(self):
        self.canvas._Canvas__image = self.previous_image
    
    def on_mouse_event(self, event) -> None:
        image = self.canvas.get_image()
        x = event.x
        y = event.y
        red = image[x,y,0]
        green = image[x,y,1]
        blue = image[x,y,2]
        self.changed_pixels.append(CanvasPixel(Point(event.x, event.y), Color(reg, green, blue)))
