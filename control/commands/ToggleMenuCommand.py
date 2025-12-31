from control.commands.Command import Command
from model.Point import Point
from view.MenuIcon import MenuIcon
from view.MenuToggleable import MenuToggleable

class ToggleMenuCommand(Command):
    def __init__(self, menu_toggleable: MenuToggleable) -> None:
        self.menu_toggleable = menu_toggleable
        self.tool_selected: MenuIcon = None
        self.point: Point = None

    def set_cursor(self, point: Point) -> None:
        self.point = point

    def get_tool_selected(self) -> MenuIcon:
        return self.tool_selected

    def execute(self) -> None:
        if self.menu_toggleable.is_toggled_on():
            menu = self.menu_toggleable.get_element()
            self.tool_selected = menu.get_icon_clicked(self.point)
        self.menu_toggleable.toggle()
    
    def undo(self) -> None:
        pass