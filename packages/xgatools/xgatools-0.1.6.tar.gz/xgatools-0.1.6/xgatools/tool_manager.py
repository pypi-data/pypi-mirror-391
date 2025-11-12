import inspect
import logging
import time

from typing import Literal, Any, Dict, Type, Callable, Optional

import xgatools.dyatona
import xgatools.non_sandbox

from xgatools.config import config
from xgatools.dyatona.sandbox_helper import DyaSandboxHelper
from xgatools.tool_base import XGATool, XGASandBoxTool, TaskContext, SandboxHelper
from xgatools.tool_list import SANDBOX_TOOL_CLASS_NAME, NO_SANDBOX_TOOL_CLASS_NAME


class XGAToolManager:
    TASK_INACTIVE_TIME = config.SANDBOX_TIMEOUT_MINUTE * 60

    def __init__(self, sandbox_type: Literal["daytona", "e2b"] = "daytona") -> None:
        self.sandbox_type = sandbox_type
        self._task_cache: Dict[str, TaskContext] = {}

        self._sandbox_helper :SandboxHelper = None
        if sandbox_type == "daytona":
            self._sandbox_helper = DyaSandboxHelper()
        elif sandbox_type == "e2b":
            pass
            # TODO: for E2B sandbox
        assert self._sandbox_helper is not None, f"XGAToolManager: Unsupported or Unrealized sandbox type: {sandbox_type}"


    async def call(self, task_id: str, tool_name: str, args: Optional[Dict[str, Any]]=None) -> Any:
        """
        Call a tool function for a specific task.

        Args:
            task_id: Unique identifier for the task
            tool_name: Name of the tool to call
            args: Arguments to pass to the tool function

        Returns:
            Result from the tool function
        """
        args = args or {}

        task_context = self._task_cache.get(task_id, None)
        if task_context is None:
            task_context = TaskContext()
            self._task_cache[task_id] = task_context
        task_context['last_call_time'] = int(time.time())

        tool_func = await self._get_tool_function(task_id, tool_name)

        result = None
        if tool_func:
            if inspect.iscoroutinefunction(tool_func):
                result = await tool_func(**args)
            else:
                result = tool_func(**args)

        return result


    async def end_task(self, task_id: str, delete_sandbox: bool = True) -> None:
        """
        End a task and clean up associated resources.

        Args:
            task_id: Task identifier to clean up
        """
        logging.info(f"XGAToolManager: End task {task_id} begin ...")
        task_context = self._task_cache.pop(task_id, None)
        if task_context is None:
            logging.warning(f"XGAToolManager: task_id: {task_id} is not in task_cache")
            return

        # Clean up sandbox
        if 'sandbox_id' in task_context and delete_sandbox:
            sandbox_id = task_context['sandbox_id']
            await self._sandbox_helper.delete_sandbox(sandbox_id)

        logging.info(f"XGAToolManager: Task {task_id} is END")


    async def _get_tool_function(self, task_id: str, tool_name: str) -> Callable | None:
        """
        Get a tool function instance for a specific task.

        Args:
            task_id: Task identifier
            tool_name: Name of the tool

        Returns:
            Callable tool function or None if not found
        """
        tool_class = self._get_tool_class(tool_name)

        if not tool_class:
            logging.warning(f"XGAToolManager: Tool class not found for tool: {tool_name}")
            return None

        # Check if we already have a tool instance for this task
        task_context = self._task_cache.get(task_id, None)
        if 'tool_instances' not in task_context:
            task_context['tool_instances'] = {}

        tool_instances = task_context['tool_instances']
        tool_instance = tool_instances.get(tool_class.__name__, None)

        if not tool_instance:
            # Create new tool instance
            if issubclass(tool_class, XGASandBoxTool):
                # Get or create sandbox for this task
                sandbox_id = await self._get_or_create_sandbox(task_id)
                if not sandbox_id:
                    logging.error(f"XGAToolManager: Could not get sandbox for task {task_id}")
                    return None
                sandbox = await  self._sandbox_helper.get_sandbox(sandbox_id)
                tool_instance = tool_class(sandbox=sandbox)
            elif issubclass(tool_class, XGATool):
                tool_instance = tool_class()
            else:
                logging.error(f"XGAToolManager: Unknown tool class type: {tool_class}")
                return None

            # Cache the tool instance
            tool_instances[tool_class.__name__] = tool_instance

        # Get the specific tool function
        tool_func = getattr(tool_instance, tool_name, None)
        if not tool_func:
            logging.warning(f"XGAToolManager: Tool function {tool_name} not found in {tool_class.__name__}")

        return tool_func


    async def _get_or_create_sandbox(self, task_id: str) -> str:
        """
        Get existing sandbox or create a new one for the task.

        Args:
            task_id: Task identifier

        Returns:
            Sandbox instance or None if creation failed
        """
        # Check if we already have a sandbox for this task
        sandbox_id = None
        task_context = self._task_cache.get(task_id, None)
        if 'sandbox_id' in task_context:
            sandbox_id = task_context['sandbox_id']
        else:
            try:
                sandbox_id = await self._sandbox_helper.create_sandbox(task_id=task_id)
                if sandbox_id:
                    task_context['sandbox_id'] = sandbox_id
            except Exception as e:
                logging.error(f"XGAToolManager: Error creating sandbox for task {task_id}: {str(e)}")

        return sandbox_id


    def _get_tool_class(self, tool_name: str) -> Type[XGATool] | Type[XGASandBoxTool] | None:
        """
        Get the tool class for a given tool name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool class or None if not found
        """
        tool_class = None

        # Check sandbox tools first
        tool_class_name = SANDBOX_TOOL_CLASS_NAME.get(tool_name, None)
        if tool_class_name:
            if self.sandbox_type == "daytona":
                if hasattr(xgatools.dyatona, '__all__') and tool_class_name in xgatools.dyatona.__all__:
                    tool_class = getattr(xgatools.dyatona, tool_class_name)
                # Fallback: try to get the class directly
                elif hasattr(xgatools.dyatona, tool_class_name):
                    tool_class = getattr(xgatools.dyatona, tool_class_name)
            elif self.sandbox_type == "e2b":
                # TODO: Implement E2B tool loading
                pass
            return tool_class

        # Check non-sandbox tools
        tool_class_name = NO_SANDBOX_TOOL_CLASS_NAME.get(tool_name, None)
        if tool_class_name:
            if hasattr(xgatools.non_sandbox, '__all__') and tool_class_name in xgatools.non_sandbox.__all__:
                tool_class = getattr(xgatools.non_sandbox, tool_class_name)
            # Fallback: try to get the class directly
            elif hasattr(xgatools.non_sandbox, tool_class_name):
                tool_class = getattr(xgatools.non_sandbox, tool_class_name)

            return tool_class

        return tool_class


    async def check_task_inactive(self):
        task_ids = list(self._task_cache.keys())
        task_ids = task_ids.copy()
        logging.info(f"XGAToolManager: Checking task inactive, {len(task_ids)} running")

        for task_id in task_ids:
            task_context = self._task_cache.get(task_id, None)
            if task_context is None:
                continue

            last_call_time = task_context['last_call_time']
            interval = int(time.time()) - last_call_time
            if interval > XGAToolManager.TASK_INACTIVE_TIME:
                logging.warning(f"XGAToolManager: Task '{task_id}' INACTIVE_TIME={interval} seconds, END TASK")
                await self.end_task(task_id, False)


    async def clean(self):
        await self._sandbox_helper.close()


if __name__ == "__main__":
    from time import sleep
    import asyncio
    from xgatools.utils.setup_env import setup_logging

    setup_logging()

    async def main() -> None:
        tool_manager = XGAToolManager()

        for i in range(2):
            task_id = f"task_{i}"
            result = await tool_manager.call(task_id=task_id, tool_name="web_search", args={"query": "gold price of 2025-9-22"})
            print(result)

            result = await tool_manager.call(task_id=task_id, tool_name="complete")
            print(result)

            print("begin sleep ..........")
            sleep(90)
            print("end sleep ..........")
            await tool_manager.check_task_inactive()

        await tool_manager.clean()


    asyncio.run(main())