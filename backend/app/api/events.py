"""Server-Sent Events (SSE) streaming API router."""

import asyncio
import json
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from app.events.bus import event_bus

router = APIRouter(prefix="/events", tags=["Events & Streaming"])


@router.get("/stream")
async def sse_event_stream(request: Request):
    """Real-time SSE event pipeline streaming events to Android client."""
    queue = await event_bus.subscribe()

    async def event_generator():
        try:
            # Send initial ping event
            yield {
                "event": "connected",
                "data": json.dumps({"status": "connected", "channel": "ai-office-live"}),
            }

            while True:
                # Check for client disconnect
                if await request.is_disconnected():
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {
                        "event": event["event"],
                        "data": json.dumps(event["data"]),
                    }
                except asyncio.TimeoutError:
                    # Emit periodic keepalive comment
                    yield {"event": "ping", "data": "keepalive"}

        finally:
            await event_bus.unsubscribe(queue)

    return EventSourceResponse(event_generator())
