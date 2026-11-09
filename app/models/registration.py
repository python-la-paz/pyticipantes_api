from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


REGISTRATION_TIMEZONE = timezone(timedelta(hours=-4))


class RegistrationPeriod(BaseModel):
    registration_start: Optional[datetime] = Field(
        default=None,
        description="Inclusive registration start in Bolivia time (UTC-04:00)",
    )
    registration_end: Optional[datetime] = Field(
        default=None,
        description="Inclusive registration end in Bolivia time (UTC-04:00)",
    )

    @field_validator("registration_start", "registration_end")
    @classmethod
    def normalize_registration_date(
        cls, value: Optional[datetime]
    ) -> Optional[datetime]:
        if value is None:
            return None
        # Preserve Bolivia wall time across MongoDB's naive datetime round trips.
        if value.tzinfo is not None:
            value = value.astimezone(REGISTRATION_TIMEZONE).replace(tzinfo=None)
        return value

    @model_validator(mode="after")
    def validate_registration_period(self) -> "RegistrationPeriod":
        if (
            self.registration_start is not None
            and self.registration_end is not None
            and self.registration_start > self.registration_end
        ):
            raise ValueError("Registration start must not be after registration end")
        return self
