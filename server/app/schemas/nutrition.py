from datetime import date as Date

from pydantic import BaseModel, Field
from .user import Read

class NutritionCreate(BaseModel):
    date: Date
    title: str = Field(min_length=1, max_length=200)
    note: str = ''


class NutritionUpdate(BaseModel):
    date: Date | None = None
    title: str | None = Field(None, min_length=1, max_length=200)
    note: str | None = None


class NutritionOut(Read):
    id: int
    athlete_id: int
    date: Date
    title: str
    note: str
