from typing import Literal

from pydantic import BaseModel, Field, field_validator

class Register(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=8, max_length=128)
    role: Literal['trainer', 'athlete']

    @field_validator('name')
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError('Имя не может быть пустым')
        return value


class Login(BaseModel):
    id: int
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshIn(BaseModel):
    refresh_token: str
