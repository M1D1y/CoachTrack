from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid import UUID

from ..core.dependencies import require_role
from ..models import Invitation, User, now


def invite_athlete(db: Session, trainer: User, athlete_public_id: UUID) -> Invitation:
    require_role(trainer, 'trainer')
    athlete = db.scalar(select(User).where(User.public_id == athlete_public_id, User.role == 'athlete').with_for_update())
    if not athlete or athlete.role != 'athlete':
        raise HTTPException(404, 'Спортсмен не найден')
    if athlete.trainer_id:
        raise HTTPException(409, 'У спортсмена уже есть тренер')
    invitation = Invitation(trainer_id=trainer.id, athlete_id=athlete.id, status='pending')
    db.add(invitation)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Ожидающее приглашение уже существует')
    db.refresh(invitation)
    return invitation


def incoming_invitations(db: Session, athlete: User) -> list[Invitation]:
    require_role(athlete, 'athlete')
    return db.scalars(select(Invitation).where(Invitation.athlete_id == athlete.id).order_by(Invitation.id.desc())).all()


def sent_invitations(db: Session, trainer: User) -> list[Invitation]:
    require_role(trainer, 'trainer')
    return db.scalars(select(Invitation).where(
        Invitation.trainer_id == trainer.id,
        Invitation.hidden_from_trainer.is_(False),
    ).order_by(Invitation.id.desc())).all()


def clear_completed_history(db: Session, trainer: User) -> None:
    require_role(trainer, 'trainer')
    db.execute(
        update(Invitation).where(
            Invitation.trainer_id == trainer.id,
            Invitation.status.in_(('accepted', 'rejected', 'cancelled')),
            Invitation.hidden_from_trainer.is_(False),
        ).values(hidden_from_trainer=True)
    )
    db.commit()


def decide_invitation(invitation_id: int, status: str, user: User, db: Session) -> Invitation:
    require_role(user, 'athlete')
    athlete = db.scalar(select(User).where(User.id == user.id).with_for_update().execution_options(populate_existing=True))
    invitation = db.scalar(
        select(Invitation).where(Invitation.id == invitation_id, Invitation.athlete_id == user.id)
        .with_for_update()
    )
    if not invitation:
        raise HTTPException(404, 'Приглашение не найдено')
    if invitation.status != 'pending':
        raise HTTPException(409, 'Приглашение уже обработано')
    if status == 'accepted':
        if athlete.trainer_id:
            raise HTTPException(409, 'У спортсмена уже есть тренер')
        athlete.trainer_id = invitation.trainer_id
        db.execute(update(Invitation).where(
            Invitation.athlete_id == user.id,
            Invitation.id != invitation.id,
            Invitation.status == 'pending',
        ).values(status='cancelled', responded_at=now()))
    invitation.status = status
    invitation.responded_at = now()
    db.commit()
    db.refresh(invitation)
    return invitation


def cancel_invitation(invitation_id: int, user: User, db: Session) -> Invitation:
    require_role(user, 'trainer')
    invitation = db.scalar(
        select(Invitation).where(Invitation.id == invitation_id, Invitation.trainer_id == user.id)
        .with_for_update()
    )
    if not invitation:
        raise HTTPException(404, 'Приглашение не найдено')
    if invitation.status != 'pending':
        raise HTTPException(409, 'Приглашение уже обработано')
    invitation.status = 'cancelled'
    invitation.responded_at = now()
    db.commit()
    return invitation
