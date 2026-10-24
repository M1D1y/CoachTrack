from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

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
