from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from services.auth import decode_access_token

bearer_scheme = HTTPBearer(
    auto_error=True,
    bearerFormat="JWT",
    scheme_name="JWTBearer",
    description=(
        "Paste only the access_token string from POST /auth/login or /auth/refresh "
        "(do not type the word Bearer; Swagger adds it). "
        "If you pasted 'Bearer …' and get 401, try again without the Bearer prefix."
    ),
)


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_factory = getattr(request.app.state, "session_factory", None)
    if session_factory is None:
        raise RuntimeError("Session factory is not available on app state")

    async with session_factory() as session:
        yield session


def _bearer_token_value(credentials: HTTPAuthorizationCredentials) -> str:
    """Normalize token if the client sent 'Bearer Bearer …' (common Swagger mistake)."""
    raw = credentials.credentials.strip()
    if raw.lower().startswith("bearer "):
        return raw[7:].strip()
    return raw


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(_bearer_token_value(credentials))
    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise credentials_error

    try:
        user_id = int(user_id_raw)
    except ValueError as exc:
        raise credentials_error from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_error

    return user
