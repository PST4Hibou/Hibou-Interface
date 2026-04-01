from functools import lru_cache
from typing import Annotated, Any
from urllib.parse import quote

from pydantic import BeforeValidator, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _parse_frontend_origins(v: Any) -> tuple[str, ...]:
    if isinstance(v, tuple):
        return v
    return tuple(o.strip() for o in str(v).split(",") if o.strip())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    database_url: str = "sqlite+aiosqlite:///./hibou.db"
    jwt_secret: str = "change-me-in-production-with-a-random-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7
    refresh_token_cookie_name: str = "refresh_token"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    frontend_origins: Annotated[
        tuple[str, ...],
        NoDecode,
        BeforeValidator(_parse_frontend_origins),
    ] = Field(
        default=(
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ),
    )
    zmq_sub_string: str = "tcp://127.0.0.1:5557"
    zmq_pub_string: str = "tcp://127.0.0.1:5556"

    vision_zmq_annotated: str = "tcp://127.0.0.1:5560"

    ptz_username: str = "admin"
    ptz_password: str = "useruser1"
    ptz_host: str = "192.168.250.30"
    ptz_video_channel: int = 1
    ptz_rtsp_port: int = 554
    #: Passed to ffmpeg -rtsp_transport. "udp" often yields lower latency on LAN than "tcp".
    ptz_rtsp_transport: str = "tcp"

    @property
    def ptz_rtsp_url(self) -> str:
        user = quote(self.ptz_username, safe="")
        password = quote(self.ptz_password, safe="")
        ch = self.ptz_video_channel
        return (
            f"rtsp://{user}:{password}@{self.ptz_host}:{self.ptz_rtsp_port}"
            f"/Streaming/Channels/10{ch}/"
        )

    @field_validator("ptz_rtsp_transport", mode="before")
    @classmethod
    def normalize_ptz_rtsp_transport(cls, v: object) -> str:
        raw = str(v or "tcp").lower()
        return raw if raw in ("tcp", "udp") else "tcp"

    @field_validator("cookie_secure", mode="before")
    @classmethod
    def parse_cookie_secure(cls, v: object) -> bool:
        if v is None or v == "":
            return False
        if isinstance(v, bool):
            return v
        return str(v).lower() in ("1", "true", "yes")

    @field_validator("cookie_samesite", mode="before")
    @classmethod
    def normalize_cookie_samesite(cls, v: object) -> str:
        raw = str(v or "lax").lower()
        if raw not in ("lax", "strict", "none"):
            return "lax"
        return raw


@lru_cache
def get_settings() -> Settings:
    return Settings()
