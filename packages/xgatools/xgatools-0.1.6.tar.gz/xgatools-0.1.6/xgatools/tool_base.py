from typing import Optional, TypedDict, Dict, Any

from mcp.types import ToolAnnotations
from dataclasses import dataclass
from abc import ABC, abstractmethod

from daytona_sdk import AsyncSandbox

class XGATool:
    pass


class XGASandBoxTool(XGATool):
    def __init__(self,  sandbox: AsyncSandbox):
        pass


class TaskContext(TypedDict, total=False):
    sandbox_id: Optional[str]
    tool_instances: Dict[str, Any]
    last_call_time: int


@dataclass
class XGAToolResult:
    success: bool
    output: str


class XGAToolNote(ToolAnnotations):
    example: Optional[str] = None


class SandboxHelper(ABC):
    @abstractmethod
    async def create_sandbox(self, task_id: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def delete_sandbox(self, sandbox_id: str):
        pass

    @abstractmethod
    async def is_sandbox_running(self, sandbox_id: str) -> bool:
        pass

    @abstractmethod
    async def get_sandbox(self, sandbox_id: str):
        pass

    @abstractmethod
    async def close(self):
        pass