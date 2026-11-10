"""FlowKit service process controller for AI Office.

Invokes controlled shell scripts to safely start, stop, restart, and inspect FlowKit.
"""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any, Dict
from app.core.logging import logger
from app.flowkit.adapter import flowkit_adapter

SCRIPT_PATH = Path(__file__).parent.parent.parent.parent / "scripts" / "flowkit_service.sh"


class FlowKitServiceManager:
    """Manages the isolated FlowKit daemon on loopback."""

    def __init__(self, script_path: Path = SCRIPT_PATH):
        self.script_path = script_path

    async def _run_command(self, action: str) -> Dict[str, Any]:
        """Execute a service management action."""
        if not self.script_path.exists():
            return {"success": False, "error": f"Script not found at {self.script_path}"}

        proc = await asyncio.create_subprocess_exec(
            str(self.script_path),
            action,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        exit_code = proc.returncode

        out_text = stdout.decode("utf-8", errors="replace").strip()
        err_text = stderr.decode("utf-8", errors="replace").strip()

        return {
            "success": exit_code == 0,
            "exit_code": exit_code,
            "stdout": out_text,
            "stderr": err_text,
        }

    async def start(self) -> Dict[str, Any]:
        return await self._run_command("start")

    async def stop(self) -> Dict[str, Any]:
        return await self._run_command("stop")

    async def restart(self) -> Dict[str, Any]:
        return await self._run_command("restart")

    async def get_status(self) -> Dict[str, Any]:
        result = await self._run_command("status")
        health = await flowkit_adapter.get_health()
        queue = await flowkit_adapter.get_queue_status()

        # Determine consolidated state
        if health.get("status") == "ok":
            if health.get("extension_connected"):
                state = "RUNNING"
            else:
                state = "WAITING_FOR_BROWSER"
        elif health.get("status") == "stopped":
            state = "STOPPED"
        elif health.get("status") == "degraded":
            state = "DEGRADED"
        else:
            state = "UNKNOWN"

        return {
            "state": state,
            "endpoint": "http://127.0.0.1:8100",
            "port": 8100,
            "websocket_port": 9222,
            "process_info": result.get("stdout"),
            "health": health,
            "queue": queue,
        }

    async def get_logs(self) -> str:
        res = await self._run_command("logs")
        return res.get("stdout", "")


flowkit_service_mgr = FlowKitServiceManager()
