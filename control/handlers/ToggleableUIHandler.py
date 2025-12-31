from view.ColorPickerToggleable import ColorPickerToggleable
from view.MenuToggleable import MenuToggleable
from view.ToggleableUI import ToggleableUI
from control.commands.PickColorCommand import PickColorCommand
from control.commands.ToggleMenuCommand import ToggleMenuCommand
from control.commands.Command import Command
from control.handlers.CommandHandler import CommandHandler
from model.Event import Event

class ToggleableUIHandler(CommandHandler):
    def __init__(self, toggleable_ui: ToggleableUI, event: Event) -> None:
        self.toggleable_ui = toggleable_ui
        self.event = event
    
    def get_command(self) -> Command:
        if isinstance(self.toggleable_ui, ColorPickerToggleable):
            match self.event.action_type:
                case self.event.action_type.LEFT_BUTTON_DOWN:
                    return PickColorCommand(self.toggleable_ui)
                case _:
                    return None
        
        elif isinstance(self.toggleable_ui, MenuToggleable):
            match self.event.action_type:
                case self.event.action_type.LEFT_BUTTON_DOWN:
                    return ToggleMenuCommand(self.toggleable_ui)
                case _:
                    return None