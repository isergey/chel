from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel


class Category(BaseModel):
    code: str
    parent: Optional[int]
    title: str
    order: int


class AgeCategory(BaseModel):
    id: int
    age: int


class Address(BaseModel):
    id: int
    parent: Optional[int]
    title: str
    address: str
    contacts: str
    geo_latitude: float
    geo_longitude: float


class Event(BaseModel):
    id: int
    avatar: str
    start_date: datetime
    end_date: datetime
    address: str
    address_reference: Optional[int]
    active: bool
    need_registration: bool
    category: List[str]
    age_category: Optional[int]
    keywords: str
    translation_html: str
    create_date: datetime
    content: str


class Response(BaseModel):
    items: List[Union[Event, Category, AgeCategory, Address]]


class Request(BaseModel):
    from_id: int
