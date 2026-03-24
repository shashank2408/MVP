"""Dataclasses shared across the product search MVP."""

from dataclasses import asdict, dataclass, field
from enum import Enum
from datetime import datetime

@dataclass
class Product:
    product_id: str
    name: str
    category: str
    price: float = 0.0
    locale: str = "en-US"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PopularitySignals:
    views: int = 0
    carts: int = 0
    sales: int = 0
    returns: int = 0


@dataclass
class EnrichedProduct(Product):
    brand: str | None = None
    tags: list[str] = field(default_factory=list)
    synonyms: list[str] = field(default_factory=list)
    search_keywords: list[str] = field(default_factory=list)
    semantic_text: str = ""
    popularity: PopularitySignals = field(default_factory=PopularitySignals)

class EventType(Enum):
    PRODUCT_CREATED = "PRODUCT_CREATED"
    PRODUCT_VIEWED = "PRODUCT_VIEWED"
    PRODUCT_ADDED_TO_CART = "PRODUCT_ADDED_TO_CART"
    PRODUCT_ADDED_TO_WISHLIST = "PRODUCT_ADDED_TO_WISHLIST"
    PRODUCT_SOLD = "PRODUCT_SOLD"
    PRODUCT_RETURNED = "PRODUCT_RETURNED"
    PRODUCT_RESTOCKED = "PRODUCT_RESTOCKED"
    PRODUCT_DISCOUNTED = "PRODUCT_DISCOUNTED"


@dataclass
class Event:
    event_id: str
    event_type: EventType
    product: Product
    timestamp: datetime
