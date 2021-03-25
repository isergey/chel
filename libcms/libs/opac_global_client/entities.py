from typing import TypeVar, Generic, List

from pydantic import BaseModel
from pydantic import Field


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int
    session_state: str
    scope: str


class Reader(BaseModel):
    login: str
    password: str = Field('', alias='pass')
    fio: str
    email: str

    class Config:
        extra = 'ignore'


T = TypeVar('T')


class ReaderResponse(BaseModel):
    type: str
    id: str
    attributes: Reader


class Meta(BaseModel):
    count: int

    class Config:
        extra = 'ignore'


class ReaderSearchResponse(BaseModel, Generic[T]):
    meta: Meta
    data: List[ReaderResponse] = []

    class Config:
        extra = 'ignore'

