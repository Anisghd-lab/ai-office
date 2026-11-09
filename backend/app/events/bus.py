"""Server-Sent Events (SSE) Event Bus for real-time telemetry."""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional
from app.core.logging import logger


class EventBus:
    """In-memory asynchronous event distributor for SSE subscribers."""

    def __init__(self):
        self._subscribers: List[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        async with self._lock:
            self._subscribers.append(queue)
        logger.info(f"New SSE client subscribed. Total active listeners: {len(self._subscribers)}")
        return queue

    async def unsubscribe(self, queue: asyncio.Queue) -> None:
        async with self._lock:
            if queue in self._subscribers:
                self._subscribers.remove(queue)
        logger.info(f"SSE client disconnected. Remaining listeners: {len(self._subscribers)}")

    async def publish(self, event_type: str, data: Dict[str, Any]) -> None:
        event = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        async with self._lock:
            for queue in self._subscribers:
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    # Drop slow consumer event to prevent memory leaks
                    pass


event_bus = EventBus()
