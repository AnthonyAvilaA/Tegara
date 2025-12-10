from view.ToggleableUI import ToggleableUI
from control.commands.PickColorCommand import PickColorCommand
from control.CommandHandler import CommandHandler
from model.Event import Event

class ToggleableUIHandler(CommandHandler):
    def __init__(self, toggleable_ui: ToggleableUI, event: Event) -> None:
        self.toggleable_ui = toggleable_ui
        self.event = event
    
    def get_command(self) -> PickColorCommand:
        match self.event.action_type:
            case self.event.action_type.LEFT_BUTTON_DOWN:
                return PickColorCommand(self.toggleable_ui)
            case self.event.action_type.RIGHT_BUTTON_DOWN:
                return PickColorCommand(self.toggleable_ui)
            case _:
                return None