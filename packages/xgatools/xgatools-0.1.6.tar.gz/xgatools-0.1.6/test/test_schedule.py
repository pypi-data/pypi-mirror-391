import asyncio
import logging
from typing import Literal

import anyio
import yaml
from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager

from xgatools.config import config
from xgatools.tool_manager import XGAToolManager
from xgatools.utils.setup_env import setup_env_logging


class XGAMcpTools:
    CHECK_TASK_TIME = 10

    sandbox_type: Literal["daytona", "e2b"] = "daytona"
    tool_manager: XGAToolManager = None

    with open("tool_schemas.yaml") as f:
        TOOL_SCHEMAS = yaml.safe_load(f)

    @classmethod
    async def periodic_task(cls):
        while True:
            try:
                await anyio.sleep(cls.CHECK_TASK_TIME)
                await XGAMcpTools.tool_manager.check_task_inactive()
            except Exception as e:
                logging.error(f"An error occurred in periodic check task: {e}")
                await anyio.sleep(cls.CHECK_TASK_TIME)

    @staticmethod
    @asynccontextmanager
    async def lifespan():
        """生命周期管理器，启动后台任务"""
        logging.info(f"Run periodic check task, TASK_INACTIVE_SECONDS is {config.TASK_INACTIVE_SECONDS} seconds")

        # 启动后台任务
        task = asyncio.create_task(XGAMcpTools.periodic_task())

        try:
            yield
        finally:
            # 清理任务
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    # 在定义完 lifespan 后创建 mcp 实例
    mcp = FastMCP(
        name="Extreme General Agent Tools",
        lifespan=lifespan
    )

    def __init__(self,
                 host: str,
                 port: int,
                 transport: Literal["stdio", "sse", "streamable-http"] = "sse",
                 sandbox_type: Literal["daytona", "e2b"] = "daytona"):
        self.transport = transport

        if transport != "stdio":
            XGAMcpTools.mcp.settings.host = host
            XGAMcpTools.mcp.settings.port = port

        XGAMcpTools.sandbox_type = sandbox_type
        XGAMcpTools.tool_manager = XGAToolManager(sandbox_type)

    def run(self):
        """同步运行方法"""
        XGAMcpTools.mcp.run(transport=self.transport)


if __name__ == "__main__":
    setup_env_logging()

    xga_mcp_tools = XGAMcpTools("localhost", 16060, "sse", "daytona")
    xga_mcp_tools.run()