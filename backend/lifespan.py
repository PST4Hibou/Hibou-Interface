from contextlib import asynccontextmanager
from fastapi import FastAPI
import zmq
import zmq.asyncio

from config import get_settings
from db import create_engine_and_session_factory
from models import Base

context = zmq.asyncio.Context()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    engine, session_factory = create_engine_and_session_factory(settings.database_url)
    app.state.db_engine = engine
    app.state.session_factory = session_factory

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind(settings.zmq_pub_bind)
    app.state.pub = pub_socket

    try:
        yield
    finally:
        pub_socket.close()
        await engine.dispose()