"""Factory that builds IndexConfig based on requested search types."""

from indexing.enriched_product_mapping import EnrichedProductMappingBuilder
from indexing.index_config import EMBEDDING_DIMENSION, IndexConfig, SearchType

_VECTOR_TYPES = {SearchType.VECTOR, SearchType.HYBRID}


class IndexConfigFactory:
    def build(self, search_types: list[SearchType]) -> IndexConfig:
        needs_vector = bool(_VECTOR_TYPES & set(search_types))

        settings: dict = {"number_of_shards": 1, "number_of_replicas": 0}
        if needs_vector:
            settings["knn"] = True

        base = EnrichedProductMappingBuilder().build()
        properties: dict = base["mappings"]["properties"]

        if needs_vector:
            properties["semantic_embedding"] = {
                "type": "knn_vector",
                "dimension": EMBEDDING_DIMENSION,
                "method": {
                    "engine": "lucene",
                    "space_type": "cosinesimil",
                    "name": "hnsw",
                    "parameters": {},
                },
            }

        return IndexConfig(settings=settings, mappings={"properties": properties})
