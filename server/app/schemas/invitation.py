from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from .user import Read

class InvitationCreate(BaseModel):
    athlete_public_id: UUID


class InvitationOut(Read):
    id: int
    trainer_public_id: UUID
    athlete_public_id: UUID
    trainer_name: str
    athlete_name: str
    status: str
    created_at: datetime
    responded_at: datetime | None
