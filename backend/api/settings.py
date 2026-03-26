from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, get_db
from models import SystemSettings, User
from schemas.settings import SystemSettingsRead, UserListRead

router = APIRouter()


@router.get("/users", response_model=list[UserListRead])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[User]:
    result = await db.execute(select(User).order_by(User.id))
    return list(result.scalars().all())


async def _get_singleton_row(db: AsyncSession) -> SystemSettings | None:
    result = await db.execute(select(SystemSettings).limit(1))
    return result.scalar_one_or_none()


@router.get("/system", response_model=SystemSettingsRead)
async def get_system_settings(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> SystemSettingsRead:
    row = await _get_singleton_row(db)
    if row is None:
        return SystemSettingsRead(latitude=None, longitude=None, angle_from_longitude=None, map_zoom=None)
    return SystemSettingsRead.model_validate(row)


@router.put("/system", response_model=SystemSettingsRead)
async def put_system_settings(
    payload: SystemSettingsRead,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> SystemSettingsRead:
    row = await _get_singleton_row(db)
    if row is None:
        row = SystemSettings(
            latitude=payload.latitude,
            longitude=payload.longitude,
            angle_from_longitude=payload.angle_from_longitude,
            map_zoom=payload.map_zoom,
        )
        db.add(row)
    else:
        row.latitude = payload.latitude
        row.longitude = payload.longitude
        row.angle_from_longitude = payload.angle_from_longitude
        row.map_zoom = payload.map_zoom
    await db.commit()
    await db.refresh(row)
    return SystemSettingsRead.model_validate(row)
