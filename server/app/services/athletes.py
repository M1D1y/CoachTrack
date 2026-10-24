from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..core.dependencies import require_role
from ..models import Invitation, User
from ..schemas.athlete import SearchUser


def prepare_search(query: str) -> tuple[int | None, tuple[str, ...]]:
    """Normalize an ID or split a name into case-insensitive search terms."""
    query = ' '.join(query.strip().split())
    if query.isascii() and query.isdecimal():
        return int(query), ()
    return None, tuple(query.split())


def search_clause(query: str):
    athlete_id, terms = prepare_search(query)
    if athlete_id is not None:
        return User.id == athlete_id
    slash = chr(92)

    def escape(term: str) -> str:
        return term.replace(slash, slash + slash).replace('%', slash + '%').replace('_', slash + '_')

    return and_(*(User.name.ilike(f'%{escape(term)}%', escape=slash) for term in terms))


def search_registered(db: Session, trainer: User, query: str) -> list[SearchUser]:
    require_role(trainer, 'trainer')
    if not query.strip():
        raise HTTPException(422, 'Укажите ID или имя')
    rows = db.scalars(select(User).where(User.role == 'athlete', search_clause(query)).order_by(User.id).limit(20)).all()
    pending_ids = set(db.scalars(select(Invitation.athlete_id).where(
        Invitation.trainer_id == trainer.id,
        Invitation.status == 'pending',
        Invitation.athlete_id.in_([athlete.id for athlete in rows]),
    )).all())
    results = []
    for athlete in rows:
        if athlete.trainer_id == trainer.id:
            status = 'team'
        elif athlete.trainer_id is not None:
            status = 'unavailable'
        elif athlete.id in pending_ids:
            status = 'pending'
        else:
            status = 'available'
        results.append(SearchUser(
            id=athlete.id, name=athlete.name, sport=athlete.sport,
            relationship_status=status,
        ))
    return results


def list_team(db: Session, trainer: User, query: str) -> list[User]:
    require_role(trainer, 'trainer')
    statement = select(User).where(User.role == 'athlete', User.trainer_id == trainer.id)
    if query.strip():
        statement = statement.where(search_clause(query))
    return db.scalars(statement.order_by(User.id)).all()
