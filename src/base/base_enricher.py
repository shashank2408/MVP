"""Base interfaces for the product search MVP."""

from abc import ABC, abstractmethod

from base.models import EnrichedProduct, Product


class BaseEnricher(ABC):
    @abstractmethod
    def enrich(self, product: Product) -> EnrichedProduct:
        """Transform a product into an enriched product."""
