from datetime import date

from pydantic import BaseModel

class Summary(BaseModel):
    week_start: date
    athlete_count: int | None = None
    training_count: int
    attended: int
    missed: int
    attendance_percent: float
