from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from data_model import Artist, Listing


class Match(BaseModel):
    artist: Artist
    listing: Listing
    score: float
    keywords: List[str]


class Matcher(ABC):
    def __init__(self, topk: int):
        self.topk = topk

    def match(self, artist: Artist, listings: List[Listing]) -> List[Match]:
        return self._batch_match([artist], listings=listings)[0]

    @abstractmethod
    def _batch_match(
        self, artists: List[Artist], listings: List[Listing]
    ) -> List[List[Match]]:
        ...
