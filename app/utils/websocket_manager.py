# app/utils/websocket_manager.py
import json
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any


class WebSocketManager:
    """
    Centralized WebSocket connection manager.
    Handles connect, disconnect, and event broadcasts for the entire app.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new client WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS CONNECTED] {len(self.active_connections)} active")

    def disconnect(self, websocket: WebSocket):
        """Remove a client WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WS DISCONNECTED] {len(self.active_connections)} remaining")

    async def broadcast(self, message: str):
        """Broadcast a plain string message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_json(self, event_type: str, payload: Dict[str, Any]):
        """
        Broadcast a structured JSON event to all clients.
        Includes timestamp + event metadata.
        """
        message = {
            "type": event_type,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        data = json.dumps(message)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

        print(f"[WS EVENT] {event_type} → {len(self.active_connections)} connections")


# ✅ Global instance (importable from anywhere)
manager = WebSocketManager()
