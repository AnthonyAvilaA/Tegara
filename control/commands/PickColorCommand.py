from control.Command import Command
from model.Point import Point
from view.ColorPickerToggleable import ColorPickerToggleable
from model.Color import Color

class PickColorCommand(Command):
    def __init__(self, color_picker_toggleable: ColorPickerToggleable) -> None:
        self.color_picker_toggleable = color_picker_toggleable
        self.point: Point = None
        self.color_selected: Color = None

    def set_cursor(self, point: Point) -> None:
        self.point = point

    def get_color_selected(self) -> Color:
        return self.color_selected

    def execute(self) -> None:
        if self.color_picker_toggleable.is_toggled_on():
            new_color = self.color_picker_toggleable.get_color_at(self.point)
            self.color_selected = new_color
        self.color_picker_toggleable.toggle()
        self.color_picker_toggleable.update_color(self.color_selected)
    
    def undo(self) -> None:
        pass