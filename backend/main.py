from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from config import get_settings
from lifespan import lifespan


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        swagger_ui_parameters={"persistAuthorization": True},
    )
    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.frontend_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    return app


app = create_app()