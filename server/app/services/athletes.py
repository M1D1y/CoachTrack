from fastapi import HTTPException
from sqlalchemy import and_, false, select
from sqlalchemy.orm import Session

from ..core.dependencies import require_role
from ..models import Invitation, User
from ..models.user import normalized_name_sql
from ..schemas.athlete import SearchUser


def prepare_search(query: str) -> tuple[int | None, tuple[str, ...]]:
    """Split a name into case-insensitive search terms."""
    query = ' '.join(query.strip().split())
    if query.isdecimal():
        return None, ()
    return None, tuple(query.split())


def search_clause(query: str):
    _, terms = prepare_search(query)
    if not terms:
        return false()
    slash = chr(92)

    def escape(term: str) -> str:
        return term.replace(slash, slash + slash).replace('%', slash + '%').replace('_', slash + '_')

    return and_(*(normalized_name_sql().like(f'%{escape(term.lower())}%', escape=slash) for term in terms))


def search_registered(db: Session, trainer: User, query: str) -> list[SearchUser]:
    require_role(trainer, 'trainer')
    normalized = ' '.join(query.split())
    if sum(character.isalpha() for character in normalized) < 3:
        raise HTTPException(422, 'Введите не менее трёх букв ФИО')
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
            public_id=athlete.public_id, name=athlete.name, sport=athlete.sport,
            relationship_status=status,
        ))
    return results


def list_team(db: Session, trainer: User, query: str) -> list[User]:
    require_role(trainer, 'trainer')
    statement = select(User).where(User.role == 'athlete', User.trainer_id == trainer.id)
    if query.strip():
        statement = statement.where(search_clause(query))
    return db.scalars(statement.order_by(User.id)).all()
