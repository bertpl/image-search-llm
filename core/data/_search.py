from dataclasses import dataclass


@dataclass
class SearchResult:
    filename: str
    score: float
    score_src: str
