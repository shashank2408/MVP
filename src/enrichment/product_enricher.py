from sentence_transformers import SentenceTransformer

from base.base_enricher import BaseEnricher
from base.models import EnrichedProduct, PopularitySignals, Product


class ProductEnricher(BaseEnricher):

    def __init__(self, tags: dict, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.tags = tags
        self.embedding_model = SentenceTransformer(model_name)

    def derive_tags(self, product: Product, tags: dict) -> tuple[str | None, list[str], list[str]]:
        tag_data = tags.get(product.product_id, {})
        brand = tag_data.get("brand")
        labels = tag_data.get("labels", [])
        synonyms = tag_data.get("synonyms", [])
        return brand, labels, synonyms

    def build_search_text(self, product: Product, labels: list[str], synonyms: list[str]) -> tuple[list[str], str]:
        keywords = [
            product.name.strip().lower(),
            product.category.lower(),
            *[label.lower() for label in labels],
            *[synonym.lower() for synonym in synonyms],
        ]
        semantic_text = " ".join(keywords)
        return keywords, semantic_text

    def normalize_locale(self, product: Product) -> str:
        return product.locale.strip()

    def enrich_product(self, product: Product) -> EnrichedProduct:
        brand, labels, synonyms = self.derive_tags(product, self.tags)
        search_keywords, semantic_text = self.build_search_text(product, labels, synonyms)
        locale = self.normalize_locale(product)

        embedding: list[float] = self.embedding_model.encode(semantic_text).tolist()

        return EnrichedProduct(
            product_id=product.product_id,
            name=product.name.strip(),
            category=product.category,
            price=product.price,
            locale=locale,
            brand=brand,
            tags=labels,
            synonyms=synonyms,
            search_keywords=search_keywords,
            semantic_text=semantic_text,
            semantic_embedding=embedding,
            popularity=PopularitySignals(),
        )

    def enrich(self, product: Product) -> EnrichedProduct:
        return self.enrich_product(product)
