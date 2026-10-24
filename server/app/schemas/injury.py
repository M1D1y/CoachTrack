from datetime import date as Date
from typing import Literal

from pydantic import BaseModel, Field
from .user import Read

class InjuryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    date: Date
    note: str = ''
    severity: Literal['mild','moderate','severe']
    status: Literal['active','healed'] = 'active'


class InjuryUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    date: Date | None = None
    note: str | None = None
    severity: Literal['mild','moderate','severe'] | None = None
    status: Literal['active','healed'] | None = None


class InjuryOut(Read):
    id: int
    athlete_id: int
    title: str
    date: Date
    note: str
    severity: str
    status: str
