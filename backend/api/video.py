from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from core.dependencies import get_current_user_media, get_current_user_websocket
from models import User
from services.vision_stream.ptz_http import stream_ptz_mjpeg

router = APIRouter()


class VisionConnectionManager:
    def __init__(self):
        self.clients: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
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

    async def broadcast(self, jpeg: bytes):
        for client in list(self.clients):
            try:
                await client.send_bytes(jpeg)
            except WebSocketDisconnect:
                self.disconnect(client)
                continue
            except Exception as e:
                print(f"[vision] error: {e}")


websocket_vision_manager = VisionConnectionManager()


@router.websocket("/stream-ws")
async def websocket_endpoint(
    ws: WebSocket,
    _user: Annotated[User, Depends(get_current_user_websocket)],
):
    await ws.accept()
    await websocket_vision_manager.connect(ws)


@router.get(
    "/ptz-mjpeg",
    response_class=StreamingResponse,
    summary="PTZ camera MJPEG (ffmpeg RTSP relay)",
)
async def ptz_mjpeg(
    _user: Annotated[User, Depends(get_current_user_media)],
):
    return StreamingResponse(
        stream_ptz_mjpeg(),
        media_type="multipart/x-mixed-replace; boundary=ffmpeg",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
