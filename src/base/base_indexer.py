"""Base indexer contract for search backends."""

from abc import ABC, abstractmethod

from base.models import EnrichedProduct


class BaseIndexer(ABC):
    @abstractmethod
    def create_index(self, index_name: str, body: dict | None = None) -> dict:
        """Create an index if it does not already exist."""

    @abstractmethod
    def index_document(
        self,
        index_name: str,
        document: EnrichedProduct,
        document_id: str | None = None,
    ) -> dict:
        """Index a single document."""

    @abstractmethod
    def bulk_index(self, index_name: str, documents: list[EnrichedProduct]) -> list[dict]:
        """Index multiple documents."""
