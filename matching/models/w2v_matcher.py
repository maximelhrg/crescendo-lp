import re
from typing import List

import gensim.downloader as api
import numpy as np
from gensim.models import Word2Vec

from data_model import Artist, Listing
from models.matcher import Match, Matcher


class Word2VecMatcher(Matcher):
    def __init__(
        self,
        topk: int,
        threshold: float = 0.8,
        checkpoint: str = "word2vec-google-news-300",
    ):
        super().__init__(topk=topk)

        try:
            self.model = Word2Vec.load(checkpoint)
        except:
            self.model = api.load(checkpoint)

        self.tokenize = lambda y: [re.sub(r"[^\w\s]", "", x).lower() for x in y.split()]
        self.threshold = threshold

    def _batch_match(
        self, artists: List[Artist], listings: List[Listing]
    ) -> List[List[Match]]:
        tokenized_listings = [
            [x for x in self.tokenize(l.description) if x in self.model]
            for l in listings
        ]
        listings_embeddings = [self.model[l] for l in tokenized_listings]
        artists_embeddings = [
            self.model[[x for x in self.tokenize(" ".join(a.tags)) if x in self.model]]
            for a in artists
        ]

        normalize = lambda x: (x / np.linalg.norm(x, axis=-1, keepdims=True))
        listings_embeddings = [normalize(x) for x in listings_embeddings]
        artists_embeddings = [normalize(x) for x in artists_embeddings]
        cosine = lambda x, y: x.dot(y.T)

        artists_matches = []
        for artist, artist_embeddings in zip(artists, artists_embeddings):
            scores = []
            keywords = []
            for listing, listing_embeddings in zip(
                tokenized_listings, listings_embeddings
            ):
                similarities = (
                    cosine(artist_embeddings, listing_embeddings) > self.threshold
                )
                listing_keywords = np.unique(
                    np.array(listing)[similarities.sum(0) > 0]
                ).tolist()
                score = ((similarities).sum(-1) > 0).sum() / len(artist_embeddings)
                scores.append(score)
                keywords.append(listing_keywords)

            matches = [
                Match(
                    artist=artist,
                    listing=listings[x],
                    score=scores[x],
                    keywords=keywords[x],
                )
                for x in np.argsort(scores)[::-1][: self.topk]
            ]
            artists_matches.append(matches)

        return artists_matches
