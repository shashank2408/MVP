"""OpenSearch-backed indexer implementation."""

from base.base_indexer import BaseIndexer
from base.models import EnrichedProduct
from clients.opensearch_client import OpenSearchClient
from indexing.index_config import IndexConfig


class OpenSearchIndexer(BaseIndexer):
    def __init__(self, client: OpenSearchClient) -> None:
        self.client = client

    def create_index(self, index_name: str, config: IndexConfig | None = None) -> dict:
        if self.client.client is None:
            self.client.connect()
        if self.client.client.indices.exists(index=index_name):
            return {"acknowledged": True, "message": f"Index '{index_name}' already exists"}
        body: dict = {}
        if config is not None:
            body = {"settings": config.settings, "mappings": config.mappings}
        return self.client.client.indices.create(index=index_name, body=body)

    def index_document(
        self,
        index_name: str,
        document: EnrichedProduct,
        document_id: str | None = None,
    ) -> dict:
        if self.client.client is None:
            self.client.connect()
        resolved_document_id = document_id or document.product_id
        return self.client.client.index(
            index=index_name,
            body=document.to_dict(),
            id=resolved_document_id,
            refresh=True,
        )

    def bulk_index(self, index_name: str, documents: list[EnrichedProduct]) -> list[dict]:
        responses: list[dict] = []
        for document in documents:
            responses.append(self.index_document(index_name, document, document_id=document.product_id))
        return responses
