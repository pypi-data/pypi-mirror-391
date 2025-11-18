from typing import Union
from pydantic import BaseModel

__all__ = [
    "PublicConfigCreateRequest",
    "PublicConfigUpdateRequest",
    "PublicConfigSetRequest",
    "PublicConfigDeleteRequest",
    "PublicConfigGetRequest",
    "PublicConfigSearchQueryRequest",
]


class PublicConfigCreateRequest(BaseModel):
    name: str
    data: dict
    tags: Union[dict, None] = None
    domain_id: str


class PublicConfigUpdateRequest(BaseModel):
    name: str
    data: Union[dict, None] = None
    tags: Union[dict, None] = None
    domain_id: str


class PublicConfigSetRequest(BaseModel):
    name: str
    data: dict
    tags: Union[dict, None] = None
    domain_id: str


class PublicConfigDeleteRequest(BaseModel):
    name: str
    domain_id: str


class PublicConfigGetRequest(BaseModel):
    name: str
    domain_id: str


class PublicConfigSearchQueryRequest(BaseModel):
    query: Union[dict, None] = None
    name: Union[str, None] = None
    domain_id: str
