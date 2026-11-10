"""FlowKit Video Engine Adapter for AI Office.

Translates AI Office autonomous production workflows into verified FlowKit operations.
Strictly connects to loopback on http://127.0.0.1:8100.
"""

import httpx
from typing import Any, Dict, List, Optional
from app.core.logging import logger


class FlowKitAdapter:
    """Modular client communicating with isolated FlowKit service."""

    def __init__(self, base_url: str = "http://127.0.0.1:8100", timeout_s: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    async def get_health(self) -> Dict[str, Any]:
        """Check FlowKit service health and browser extension connection."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                resp = await client.get(f"{self.base_url}/health")
                if resp.status_code == 200:
                    return resp.json()
                return {
                    "status": "degraded",
                    "http_code": resp.status_code,
                    "extension_connected": False,
                }
        except httpx.ConnectError:
            return {
                "status": "stopped",
                "error": "FlowKit service is not running or unreachable on port 8100",
                "extension_connected": False,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "extension_connected": False,
            }

    async def create_project(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new video production project in FlowKit."""
        payload = {"name": name}
        if description:
            payload["description"] = description

        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            resp = await client.post(f"{self.base_url}/api/projects", json=payload)
            if resp.status_code in (200, 201):
                return resp.json()
            raise RuntimeError(f"FlowKit project creation failed: HTTP {resp.status_code} - {resp.text}")

    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all production projects in FlowKit."""
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            resp = await client.get(f"{self.base_url}/api/projects")
            if resp.status_code == 200:
                data = resp.json()
                return data if isinstance(data, list) else data.get("projects", [])
            return []

    async def create_scene(
        self,
        project_id: str,
        scene_number: int,
        visual_prompt: str,
        duration_s: float = 4.0,
        narration: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a scene within a FlowKit project."""
        payload = {
            "project_id": project_id,
            "scene_number": scene_number,
            "visual_prompt": visual_prompt,
            "duration": duration_s,
        }
        if narration:
            payload["narration"] = narration

        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            resp = await client.post(f"{self.base_url}/api/scenes", json=payload)
            if resp.status_code in (200, 201):
                return resp.json()
            raise RuntimeError(f"FlowKit scene creation failed: HTTP {resp.status_code} - {resp.text}")

    async def get_queue_status(self) -> Dict[str, Any]:
        """Fetch FlowKit background generation queue status."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                resp = await client.get(f"{self.base_url}/api/requests")
                if resp.status_code == 200:
                    requests = resp.json()
                    pending = [r for r in requests if r.get("status") == "PENDING"]
                    processing = [r for r in requests if r.get("status") == "PROCESSING"]
                    completed = [r for r in requests if r.get("status") == "COMPLETED"]
                    failed = [r for r in requests if r.get("status") == "FAILED"]
                    return {
                        "total": len(requests),
                        "pending": len(pending),
                        "processing": len(processing),
                        "completed": len(completed),
                        "failed": len(failed),
                        "requests": requests[:20],
                    }
                return {"total": 0, "pending": 0, "processing": 0, "completed": 0, "failed": 0, "requests": []}
        except Exception as e:
            logger.warning(f"Failed to fetch FlowKit queue: {e}")
            return {"error": str(e), "total": 0, "pending": 0, "processing": 0, "completed": 0, "failed": 0}

    async def assemble_video(
        self,
        project_id: str,
        target_duration_s: Optional[int] = None,
        orientation: str = "vertical",
    ) -> Dict[str, Any]:
        """Trigger FFmpeg assembly of generated scenes into a final video."""
        payload: Dict[str, Any] = {
            "project_id": project_id,
            "orientation": orientation,
        }
        if target_duration_s:
            payload["target_duration_s"] = target_duration_s

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/api/videos/assemble", json=payload)
            if resp.status_code in (200, 201):
                return resp.json()
            raise RuntimeError(f"Video assembly failed: HTTP {resp.status_code} - {resp.text}")


flowkit_adapter = FlowKitAdapter()
