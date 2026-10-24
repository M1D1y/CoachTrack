from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .core.config import settings

app = FastAPI(
    title='CoachTrack API',
    version='1.0.0',
    description='API учебного приложения тренера и спортсмена',
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings().cors_origins.split(',') if origin.strip()],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(api_router, prefix='/api/v1')
