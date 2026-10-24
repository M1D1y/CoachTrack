from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.dependencies import current_user
from ..db.session import get_db
from ..models import User
from ..schemas.invitation import InvitationCreate, InvitationOut
from ..services.invitations import (
    cancel_invitation, decide_invitation, incoming_invitations,
    invite_athlete, sent_invitations,
)

router = APIRouter()


@router.post('/invitations', response_model=InvitationOut, status_code=201, tags=['invitations'])
def invite(body: InvitationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return invite_athlete(db, user, body.athlete_id)


@router.get('/invitations/incoming', response_model=list[InvitationOut], tags=['invitations'])
def incoming(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return incoming_invitations(db, user)


@router.get('/invitations/sent', response_model=list[InvitationOut], tags=['invitations'])
def sent(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return sent_invitations(db, user)


@router.post('/invitations/{invitation_id}/accept', response_model=InvitationOut, tags=['invitations'])
def accept(invitation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return decide_invitation(invitation_id, 'accepted', user, db)


@router.post('/invitations/{invitation_id}/reject', response_model=InvitationOut, tags=['invitations'])
def reject(invitation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return decide_invitation(invitation_id, 'rejected', user, db)


@router.post('/invitations/{invitation_id}/cancel', response_model=InvitationOut, tags=['invitations'])
def cancel(invitation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return cancel_invitation(invitation_id, user, db)
