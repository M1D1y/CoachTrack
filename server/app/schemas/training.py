from datetime import date as Date, datetime, time as Time
from typing import Literal

from pydantic import BaseModel, Field
from .user import Read

class TrainingCreate(BaseModel):
    athlete_id: int
    date: Date
    time: Time
    duration_minutes: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str = ''


class TrainingUpdate(BaseModel):
    date: Date | None = None
    time: Time | None = None
    duration_minutes: int | None = Field(None, gt=0)
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None


class AttendanceUpdate(BaseModel):
    attendance: Literal['planned','attended','missed']


class TrainingOut(Read):
    id: int
    athlete_id: int
    date: Date
    time: Time
    duration_minutes: int
    title: str
    description: str
    attendance: str
    created_at: datetime
