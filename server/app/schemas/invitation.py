from datetime import datetime

from pydantic import BaseModel
from .user import Read

class InvitationCreate(BaseModel):
    athlete_id: int


class InvitationOut(Read):
    id: int
    trainer_id: int
    athlete_id: int
    status: str
    created_at: datetime
    responded_at: datetime | None
