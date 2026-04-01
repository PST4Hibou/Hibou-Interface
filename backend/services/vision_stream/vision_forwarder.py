import asyncio

import cv2
import zmq.asyncio

from api.video import websocket_vision_manager
from core.config import get_settings

settings = get_settings()


def frame_to_jpeg_bytes(frame) -> bytes:
    """Encode H×W×3 uint8 array as JPEG. OpenCV expects BGR; convert if your source is RGB."""
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    if not ok:
        raise ValueError("cv2.imencode failed")
    return buf.tobytes()

class ZMQVisionForwarder:
    def __init__(self):
        self.context = zmq.asyncio.Context()
        self.socket_annotated = self.context.socket(zmq.SUB)
        self.socket_annotated.setsockopt(zmq.SUBSCRIBE, b"")
        self.socket_annotated.connect(settings.vision_zmq_annotated)

    async def forwarder(self):
        while True:
            try:
                frame = await self.socket_annotated.recv_pyobj()
                print(f"[vision] received raw frame: {frame.shape}")
                jpeg = frame_to_jpeg_bytes(frame)
                await websocket_vision_manager.broadcast(jpeg)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[vision] error: {e}")