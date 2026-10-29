from typing import Literal

from pydantic import BaseModel, Field, field_validator
from ..core.names import full_name, normalize_name, validate_name_part

class Register(BaseModel):
    last_name: str = Field(min_length=1, max_length=60)
    first_name: str = Field(min_length=1, max_length=60)
    patronymic: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=8, max_length=128)
    role: Literal['trainer', 'athlete']

    @field_validator('last_name', 'first_name', 'patronymic', mode='before')
    @classmethod
    def clean_name_part(cls, value: str) -> str:
        return validate_name_part(value) if isinstance(value, str) else value

    @property
    def full_name(self) -> str:
        return full_name(self.last_name, self.first_name, self.patronymic)


class Login(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    password: str

    @field_validator('name', mode='before')
    @classmethod
    def clean_name(cls, value: str) -> str:
        return normalize_name(value) if isinstance(value, str) else value


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshIn(BaseModel):
    refresh_token: str
