from typing import List, Optional

from pydantic import BaseModel


class Artist(BaseModel):
    uid: Optional[str] = None
    name: str
    art: str
    tags: List[str]
    country: str


class Listing(BaseModel):
    uid: Optional[str] = None
    description: str
    country: str
    tags: Optional[List[str]] = None
