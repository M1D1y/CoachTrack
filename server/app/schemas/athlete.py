from .user import Read
from uuid import UUID

class SearchUser(Read):
    public_id: UUID
    name: str
    sport: str | None
    relationship_status: str
