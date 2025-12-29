import definitions.Tools as Tools
from control.handlers.CommandHandler import CommandHandler
from control.ToolStatus import ToolStatus
from control.commands.SetToolCommand import SetToolCommand

class MenuIconHandler(CommandHandler):
    def __init__(self, tool_status: ToolStatus, tool: Tools) -> None:
        self.tool_status = tool_status
        self.tool = tool
    
    def get_command(self):
        return SetToolCommand(self.tool_status, self.tool)
