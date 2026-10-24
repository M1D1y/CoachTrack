from fastapi import APIRouter

from . import auth, users, athletes, invitations, team, trainings, injuries, nutrition, reports

api_router = APIRouter()

for module in (auth, users, athletes, invitations, team, trainings, injuries, nutrition, reports):
    api_router.include_router(module.router)
