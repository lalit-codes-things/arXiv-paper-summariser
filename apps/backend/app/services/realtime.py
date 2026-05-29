from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active: dict[str, list[WebSocket]] = {}

    async def connect(self, workspace_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.setdefault(workspace_id, []).append(websocket)

    def disconnect(self, workspace_id: str, websocket: WebSocket) -> None:
        sockets = self.active.get(workspace_id, [])
        if websocket in sockets:
            sockets.remove(websocket)

    async def broadcast(self, workspace_id: str, event: dict) -> None:
        for websocket in list(self.active.get(workspace_id, [])):
            await websocket.send_json(event)


manager = ConnectionManager()
