import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.config import get_settings
from core.db import create_engine_and_session_factory, sqlite_add_missing_columns
from models import Base
from services.ipc_forwarder.zeromq import ZMQForwarder
from services.vision_stream.vision_forwarder import ZMQVisionForwarder


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    engine, session_factory = create_engine_and_session_factory(settings.database_url)
    app.state.db_engine = engine
    app.state.session_factory = session_factory

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.run_sync(sqlite_add_missing_columns)

    """Start ZeroMQ IPC forwarder and annotated vision ingest (ZMQ → WebSocket)."""
    ipc_forwarder_task = asyncio.create_task(ZMQForwarder().forwarder())
    vision_forwarder_task = asyncio.create_task(ZMQVisionForwarder().forwarder())

    try:
        yield
    finally:
        ipc_forwarder_task.cancel()
        vision_forwarder_task.cancel()
        await asyncio.gather(
            ipc_forwarder_task,
            vision_forwarder_task,
            return_exceptions=True,
        )
        await engine.dispose()