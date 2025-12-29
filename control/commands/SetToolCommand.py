from definitions.Tools import Tools
from control.commands.Command import Command
from control.ToolStatus import ToolStatus

class SetToolCommand(Command):
    def __init__(self, tool_status: ToolStatus, tool: Tools) -> None:
        self.tool_status = tool_status
        self.tool = tool

    def execute(self) -> None:
        self.tool_status.set_tool(self.tool)