from .user import Read

class SearchUser(Read):
    id: int
    name: str
    sport: str | None
    relationship_status: str
