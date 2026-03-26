"""OpenSearch search methods: keyword, fuzzy, phrase, vector, hybrid."""

from sentence_transformers import SentenceTransformer

from clients.opensearch_client import OpenSearchClient

_SEARCH_FIELDS = ["name", "category", "semantic_text", "tags", "brand"]


class OpenSearchSearcher:
    def __init__(
        self,
        client: OpenSearchClient,
        index_name: str,
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.client = client
        self.index_name = index_name
        self.embedding_model = SentenceTransformer(model_name)

    def keyword(self, q: str, size: int = 10) -> list[dict]:
        query = {
            "query": {
                "multi_match": {
                    "query": q,
                    "fields": _SEARCH_FIELDS,
                }
            },
            "size": size,
        }
        return self._execute(query)

    def fuzzy(self, q: str, size: int = 10) -> list[dict]:
        query = {
            "query": {
                "multi_match": {
                    "query": q,
                    "fields": _SEARCH_FIELDS,
                    "fuzziness": "AUTO",
                }
            },
            "size": size,
        }
        return self._execute(query)

    def phrase(self, q: str, size: int = 10) -> list[dict]:
        query = {
            "query": {
                "match_phrase": {
                    "semantic_text": q,
                }
            },
            "size": size,
        }
        return self._execute(query)

    def vector(self, q: str, size: int = 10) -> list[dict]:
        embedding: list[float] = self.embedding_model.encode(q).tolist()
        query = {
            "query": {
                "knn": {
                    "semantic_embedding": {
                        "vector": embedding,
                        "k": size,
                    }
                }
            },
            "size": size,
        }
        return self._execute(query)

    def hybrid(self, q: str, size: int = 10) -> list[dict]:
        embedding: list[float] = self.embedding_model.encode(q).tolist()
        query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": q,
                                "fields": _SEARCH_FIELDS,
                                "boost": 1.0,
                            }
                        },
                        {
                            "knn": {
                                "semantic_embedding": {
                                    "vector": embedding,
                                    "k": size,
                                    "boost": 2.0,
                                }
                            }
                        },
                    ]
                }
            },
            "size": size,
        }
        return self._execute(query)

    def _execute(self, query: dict) -> list[dict]:
        if self.client.client is None:
            self.client.connect()
        response = self.client.client.search(index=self.index_name, body=query)
        return [hit["_source"] for hit in response["hits"]["hits"]]
