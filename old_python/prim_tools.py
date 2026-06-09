"""
Prim Development Tools
Provides build tools, testing tools, debugging tools,
code analysis, and developer utilities.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ToolType(Enum):
    """Tool types"""
    COMPILER = "compiler"
    LINKER = "linker"
    DEBUGGER = "debugger"
    TESTER = "tester"


@dataclass
class Tool:
    """Development tool"""
    name: str
    type: ToolType
    path: str


class ToolManager:
    """Tool manager"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def add_tool(self, tool: Tool):
        """Add tool"""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool"""
        return self.tools.get(name)


def main():
    print("Testing Development Tools...")
    manager = ToolManager()
    tool = Tool(name="gcc", type=ToolType.COMPILER, path="/usr/bin/gcc")
    manager.add_tool(tool)
    print(f"Tool: {tool.name}")
    print("Development Tools initialized successfully")


if __name__ == "__main__":
    main()
