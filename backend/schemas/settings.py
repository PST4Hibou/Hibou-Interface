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

    @model_validator(mode="after")
    def validate_coordinates(self) -> "SystemSettingsRead":
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            msg = "latitude must be between -90 and 90"
            raise ValueError(msg)
        if self.longitude is not None and not -180 <= self.longitude <= 180:
            msg = "longitude must be between -180 and 180"
            raise ValueError(msg)
        return self
