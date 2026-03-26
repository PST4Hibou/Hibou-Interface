from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class UserListRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    identifier: str
    created_at: datetime


class SystemSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latitude: float | None
    longitude: float | None
    angle_from_longitude: float | None
    map_zoom: float | None
    map_pitch: float | None = None
    map_3d_buildings: bool | None = None
    mapbox_style: str | None = None

    @model_validator(mode="after")
    def validate_coordinates(self) -> "SystemSettingsRead":
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            msg = "latitude must be between -90 and 90"
            raise ValueError(msg)
        if self.longitude is not None and not -180 <= self.longitude <= 180:
            msg = "longitude must be between -180 and 180"
            raise ValueError(msg)
        if self.map_pitch is not None and not 0 <= self.map_pitch <= 85:
            msg = "map_pitch must be between 0 and 85"
            raise ValueError(msg)
        return self
