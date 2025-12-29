from definitions.Tools import Tools

class ToolStatus:
    def __init__(self, tool: Tools = Tools.PENCIL) -> None:
        self.current_tool: Tools = tool
    
    def set_tool(self, tool: Tools) -> None:
        self.current_tool = tool
    
    def get_tool(self) -> Tools:
        return self.current_tool