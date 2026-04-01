
from fastapi import WebSocket, WebSocketDisconnect

from fastapi import APIRouter

router = APIRouter()

class VisionConnectionManager:
    def __init__(self):
        self.clients: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        print(f"[vision] client connected: {ws.client.host}")
        self.clients.append(ws)

        while True:
            try:
                data = await ws.receive_text()
            except WebSocketDisconnect:
                self.disconnect(ws)
                break

    def disconnect(self, ws: WebSocket):
        self.clients.remove(ws)

    async def broadcast(self, frame: bytes):
        for client in self.clients:
            try:
                print(f"[vision] sending frame to client: {len(frame)}")
                await client.send_bytes(frame)
            except WebSocketDisconnect:
                self.disconnect(client)
                break
            except Exception as e:
                print(f"[vision] error: {e}")
                pass

websocket_vision_manager = VisionConnectionManager()

@router.websocket("/stream-ws")
async def websocket_endpoint(ws: WebSocket):
    await websocket_vision_manager.connect(ws)
