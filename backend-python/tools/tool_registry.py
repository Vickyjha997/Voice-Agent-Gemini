"""Tool Registry - Register all available function calling tools"""
from typing import Dict, Any, Callable, List, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import FunctionResult


class ToolDefinition:
    """Definition of a tool/function"""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler


class ToolRegistry:
    """Registry for function calling tools"""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
    
    def register(self, tool: ToolDefinition):
        """Register a tool"""
        self.tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def get_all(self) -> List[ToolDefinition]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    async def execute(self, name: str, args: Dict[str, Any]) -> FunctionResult:
        """Execute a tool"""
        tool = self.tools.get(name)
        if not tool:
            return FunctionResult(
                call_id='',
                result=None,
                error=f"Tool {name} not found"
            )
        
        try:
            # Check if handler is async
            if callable(tool.handler):
                import asyncio
                if asyncio.iscoroutinefunction(tool.handler):
                    result = await tool.handler(args)
                else:
                    result = tool.handler(args)
            else:
                result = None
            
            return FunctionResult(
                call_id='',
                result=result
            )
        except Exception as e:
            return FunctionResult(
                call_id='',
                result=None,
                error=str(e)
            )
    
    def get_gemini_tools_format(self) -> List[Dict[str, Any]]:
        """Get tools in Gemini API format"""
        return [
            {
                'name': tool.name,
                'description': tool.description,
                'parameters': tool.parameters
            }
            for tool in self.get_all()
        ]


# Global instance
tool_registry = ToolRegistry()

