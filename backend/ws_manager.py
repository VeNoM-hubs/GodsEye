import json
import logging
from typing import List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, payload: dict):
        # Collect dead connections first — never mutate the list mid-iteration
        dead = []
        for ws in self.active_connections:
            try:
                await ws.send_text(json.dumps(payload, default=str))
            except Exception as exc:
                logger.debug("WS send failed, marking connection dead: %s", exc)
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws)


manager = ConnectionManager()
