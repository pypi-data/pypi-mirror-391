import logging

from typing import override, Optional

from daytona_sdk import (
    AsyncDaytona,
    DaytonaConfig,
    CreateSandboxFromSnapshotParams,
    AsyncSandbox,
    SessionExecuteRequest,
    Resources,
    SandboxState
)

from xgatools.tool_base import SandboxHelper
from xgatools.config import config

class DyaSandboxHelper(SandboxHelper):
    def __init__(self):
        sandbox_config = config.get_daytona_config()

        self._sandbox_image_name = sandbox_config['image_name']

        timeout = sandbox_config['timeout']
        self._auto_stop_interval = timeout if timeout > 0 else 1

        logging.warning(f"DyaSandbox will AUTO STOP after {self._auto_stop_interval} minutes, then AUTO DELETE after 1 minutes")

        self.daytona = AsyncDaytona(DaytonaConfig(
            api_key = sandbox_config['api_key'],
            api_url = sandbox_config['server_url'],
            target = sandbox_config['target'],
        ))

    @override
    async def get_sandbox(self, sandbox_id: str) -> AsyncSandbox:
        sandbox = None
        if sandbox_id:
            sandbox = await self.daytona.get(sandbox_id)
        return sandbox


    @override
    async def create_sandbox(self, task_id: Optional[str] = None) -> str:
        """Create a new sandbox with all required services configured and running."""
        # Generate a password for the sandbox
        import secrets
        import string
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

        logging.debug("Creating new Daytona sandbox environment")
        logging.debug("Configuring sandbox with snapshot and environment variables")

        labels = None
        if task_id:
            logging.debug(f"Using sandbox_id as label: {task_id}")
            labels = {'id': task_id}

        params = CreateSandboxFromSnapshotParams(
            snapshot    = self._sandbox_image_name,
            public      = True,
            labels      = labels,
            resources   = Resources(cpu=1, memory=3, disk=5),
            auto_stop_interval      = self._auto_stop_interval,
            auto_delete_interval    = 1,
            env_vars={
                "CHROME_PERSISTENT_SESSION" : "true",
                "RESOLUTION"                : "1024x768x24",
                "RESOLUTION_WIDTH"          : "1024",
                "RESOLUTION_HEIGHT"         : "768",
                "VNC_PASSWORD"              : password,
                "ANONYMIZED_TELEMETRY"      : "false",
                "CHROME_PATH"               : "",
                "CHROME_USER_DATA"          : "",
                "CHROME_DEBUGGING_PORT"     : "9222",
                "CHROME_DEBUGGING_HOST"     : "localhost",
                "CHROME_CDP"                : ""
            },
        )

        # Create the sandbox
        sandbox = await self.daytona.create(params)
        # print("*"*100)
        # print(sandbox.get_preview_link)
        logging.info(f"Sandbox created with ID: {sandbox.id}")

        # Start supervisord in a session for new sandbox
        await self._start_supervisord_session(sandbox)

        logging.info(f"Sandbox environment successfully initialized")
        return sandbox.id


    async def _start_supervisord_session(self, sandbox: AsyncSandbox):
        """Start supervisord in a session."""
        session_id = "supervisord-session"
        try:
            logging.info(f"Creating session {session_id} for supervisord")
            await sandbox.process.create_session(session_id)

            # Execute supervisord command
            await sandbox.process.execute_session_command(session_id, SessionExecuteRequest(
                command="exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf",
                run_async=True
            ))
            logging.info(f"Supervisord started in session {session_id}")
        except Exception as e:
            logging.error(f"Error starting supervisord session: {str(e)}")
            raise e


    @override
    async def delete_sandbox(self, sandbox_id: str):
        try:
            if sandbox_id:
                sandbox = await self.daytona.get(sandbox_id)
                await self.daytona.delete(sandbox)

            logging.info(f"Successfully deleted sandbox {sandbox_id}")
        except Exception as e:
            logging.error(f"Error deleting sandbox {sandbox_id}: {str(e)}")


    @override
    async def is_sandbox_running(self, sandbox_id: str) -> bool:
        sandbox = await self.daytona.get(sandbox_id)
        return sandbox and sandbox.state == SandboxState.STARTED

    @override
    async def close(self):
        try:
            logging.warning("CLOSE SANDBOX ENVIRONMENT")
            await self.daytona.close()
        except Exception as e:
            logging.error(f"Error closing daytona sandbox: {str(e)}")



if __name__ == "__main__":
    from xgatools.utils.setup_env import setup_logging
    from uuid import uuid4
    import asyncio
    setup_logging()

    async def main():
        task_id = f"task_{uuid4()}"
        dya_sandbox_helper = DyaSandboxHelper()
        sandbox_id = await dya_sandbox_helper.create_sandbox(task_id)
        await dya_sandbox_helper.delete_sandbox(sandbox_id)
        await dya_sandbox_helper.daytona.close()

    asyncio.run(main())