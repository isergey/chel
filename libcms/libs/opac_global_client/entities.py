from datetime import datetime, date
from typing import TypeVar, Generic, List

from pydantic import BaseModel, validator
from pydantic import Field


def to_camel(string: str) -> str:
    parts = string.split('_')
    length = len(parts)

    if not length:
        return ''

    if length == 1:
        return parts[0]

    return parts[0] + ''.join(word.capitalize() for word in string.split('_')[1:])


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
    count: str

    class Config:
        extra = 'ignore'


class ReaderSearchResponse(BaseModel, Generic[T]):
    meta: Meta
    data: List[ReaderResponse] = []

    class Config:
        extra = 'ignore'


class CirculationOperation(BaseModel):
    circulation_record_id: str
    reader_id: str
    place: str
    place_name: str
    operation: str
    method: str
    db_id: str
    record_id: str
    item_code: str
    item_inventory_number: str
    operation_time: datetime
    next_operation_time: date

    class Config:
        extra = 'ignore'
        alias_generator = to_camel

    @validator('operation_time', pre=True)
    def operation_time_validate(cls, v):
        return datetime.strptime(v, '%d.%m.%Y %H:%M:%S')

    @validator('next_operation_time', pre=True)
    def next_operation_time_validate(cls, v):
        return datetime.strptime(v, '%d.%m.%Y').date()



class CirculationOperationInfo(BaseModel):
    type: str
    id: str
    attributes: CirculationOperation


class CirculationOperationsResponse(BaseModel):
    meta: Meta
    data: List[CirculationOperationInfo] = []

    class Config:
        extra = 'ignore'
        alias_generator = to_camel
