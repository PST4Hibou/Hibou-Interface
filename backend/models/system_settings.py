from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from models.user import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    angle_from_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    map_zoom: Mapped[float | None] = mapped_column(Float, nullable=True)
    map_pitch: Mapped[float | None] = mapped_column(Float, nullable=True)
    map_3d_buildings: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    mapbox_style: Mapped[str | None] = mapped_column(String(32), nullable=True)
