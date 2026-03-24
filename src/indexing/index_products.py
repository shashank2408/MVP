import argparse
import json
from pathlib import Path

from base.models import EnrichedProduct, PopularitySignals, Product
from clients.opensearch_client import OpenSearchClient
from indexing.enriched_product_mapping import EnrichedProductMappingBuilder
from indexing.opensearch_indexer import OpenSearchIndexer


def to_enriched_product(product: Product, payload: dict) -> EnrichedProduct:
    popularity_payload = payload.get("popularity", {})
    popularity = PopularitySignals(
        views=popularity_payload.get("views", 0),
        carts=popularity_payload.get("carts", 0),
        sales=popularity_payload.get("sales", 0),
        returns=popularity_payload.get("returns", 0),
    )

    return EnrichedProduct(
        product_id=product.product_id,
        name=product.name,
        category=product.category,
        price=product.price,
        locale=product.locale,
        brand=payload.get("brand"),
        tags=payload.get("tags", []),
        synonyms=payload.get("synonyms", []),
        search_keywords=payload.get("search_keywords", []),
        semantic_text=payload.get("semantic_text", ""),
        popularity=popularity,
    )


def load_products(path: str) -> list[EnrichedProduct]:
    with Path(path).open("r", encoding="utf-8") as f:
        products = json.load(f)
    if not isinstance(products, list):
        raise ValueError("Enriched products file must contain a JSON array")

    enriched_products: list[EnrichedProduct] = []
    for payload in products:
        product = Product(
            product_id=payload["product_id"],
            name=payload["name"],
            category=payload["category"],
            price=payload.get("price", 0.0),
            locale=payload.get("locale", "en-US"),
        )
        enriched_products.append(to_enriched_product(product, payload))

    return enriched_products


def main() -> None:
    parser = argparse.ArgumentParser(description="Index enriched products into OpenSearch")
    parser.add_argument("--input", required=True, help="Path to enriched products JSON file")
    parser.add_argument("--index", default="products", help="OpenSearch index name")
    parser.add_argument("--host", default="localhost", help="OpenSearch host")
    parser.add_argument("--port", type=int, default=9200, help="OpenSearch port")
    args = parser.parse_args()

    products = load_products(args.input)

    client = OpenSearchClient(host=args.host, port=args.port)
    indexer = OpenSearchIndexer(client)
    mapping_builder = EnrichedProductMappingBuilder()

    if not client.health_check():
        raise ConnectionError(f"OpenSearch is not reachable at {args.host}:{args.port}")

    indexer.create_index(args.index, mapping_builder.build())
    responses = indexer.bulk_index(args.index, products)

    print(f"Indexed {len(responses)} documents into '{args.index}' from {args.input}")


if __name__ == "__main__":
    main()
