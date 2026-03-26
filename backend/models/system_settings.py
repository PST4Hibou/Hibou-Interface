from sqlalchemy import Float
from sqlalchemy.orm import Mapped, mapped_column

from models.user import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    angle_from_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    map_zoom: Mapped[float | None] = mapped_column(Float, nullable=True)
