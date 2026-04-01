"""PTZ RTSP → MJPEG over HTTP via ffmpeg (separate from ZMQ → WebSocket annotated pipeline)."""

import asyncio
from collections.abc import AsyncIterator

from core.config import get_settings


async def stream_ptz_mjpeg() -> AsyncIterator[bytes]:
    """Yield multipart MJPEG bytes (Content-Type: multipart/x-mixed-replace; boundary=ffmpeg)."""
    settings = get_settings()
    rtsp_url = settings.ptz_rtsp_url
    transport = settings.ptz_rtsp_transport

    # Avoid stderr=PIPE without reading it: when the pipe fills (~64 KiB), ffmpeg blocks and stalls
    # the stream for seconds.
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-rtsp_transport",
        transport,
        "-fflags",
        "nobuffer+fastseek+discardcorrupt",
        "-flags",
        "low_delay",
        "-analyzeduration",
        "0",
        "-probesize",
        "32",
        "-max_delay",
        "0",
        "-reorder_queue_size",
        "0",
        "-i",
        rtsp_url,
        "-an",
        "-fps_mode",
        "passthrough",
        "-c:v",
        "mjpeg",
        "-q:v",
        "5",
        "-f",
        "mpjpeg",
        "-",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        assert proc.stdout is not None
        while True:
            chunk = await proc.stdout.read(65536)
            if not chunk:
                break
            yield chunk
    finally:
        proc.kill()
        await proc.wait()
