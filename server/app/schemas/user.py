from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator
from ..core.names import validate_full_name

class Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserOut(Read):
    id: int
    name: str
    role: str
    age: int | None
    sport: str | None
    trainer_id: int | None
    created_at: datetime


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    age: int | None = Field(None, ge=0, le=120)
    sport: str | None = Field(None, max_length=100)

    @field_validator('name', mode='before')
    @classmethod
    def full_name_required(cls, value: str | None) -> str | None:
        return validate_full_name(value) if isinstance(value, str) else value
