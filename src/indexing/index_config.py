"""Index configuration dataclass and search type definitions."""

from dataclasses import dataclass
from enum import Enum


EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2


class SearchType(Enum):
    KEYWORD = "keyword"
    FUZZY = "fuzzy"
    PHRASE = "phrase"
    VECTOR = "vector"
    HYBRID = "hybrid"


@dataclass
class IndexConfig:
    settings: dict
    mappings: dict  # {"properties": {...}}
