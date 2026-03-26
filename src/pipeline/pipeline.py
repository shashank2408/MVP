"""Shared wiring helpers for the pipeline entrypoints."""

import json
from pathlib import Path

from clients.kafka_client import KafkaClient, KafkaClientType
from clients.opensearch_client import OpenSearchClient
from enrichment.product_enricher import ProductEnricher
from indexing.index_config import SearchType
from indexing.index_config_factory import IndexConfigFactory
from indexing.opensearch_indexer import OpenSearchIndexer
from pipeline.product_event_consumer import ProductEventConsumer
from pipeline.product_event_producer import ProductEventProducer


def load_json_file(path: str) -> object:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_tags(path: str) -> dict:
    payload = load_json_file(path)
    if not isinstance(payload, dict):
        raise ValueError("Tags file must contain a JSON object")
    return payload


def load_events(path: str) -> list[dict]:
    payload = load_json_file(path)
    if not isinstance(payload, list):
        raise ValueError("Events file must contain a JSON array")
    return payload


def build_producer(topic: str, bootstrap_servers: str) -> ProductEventProducer:
    kafka_client = KafkaClient(
        client_type=KafkaClientType.PRODUCER,
        bootstrap_servers=bootstrap_servers,
        topic=topic,
    )
    return ProductEventProducer(kafka_client=kafka_client, topic=topic)


def build_consumer(
    topic: str,
    bootstrap_servers: str,
    consumer_group: str,
    tags_path: str,
    index_name: str,
    opensearch_host: str,
    opensearch_port: int,
) -> ProductEventConsumer:
    kafka_client = KafkaClient(
        client_type=KafkaClientType.CONSUMER,
        bootstrap_servers=bootstrap_servers,
        topic=topic,
        group_id=consumer_group,
    )
    enricher = ProductEnricher(load_tags(tags_path))
    opensearch_client = OpenSearchClient(host=opensearch_host, port=opensearch_port)
    indexer = OpenSearchIndexer(opensearch_client)
    index_config = IndexConfigFactory().build([
        SearchType.KEYWORD,
        SearchType.FUZZY,
        SearchType.PHRASE,
        SearchType.VECTOR,
        SearchType.HYBRID,
    ])

    if not opensearch_client.health_check():
        raise ConnectionError(f"OpenSearch is not reachable at {opensearch_host}:{opensearch_port}")

    indexer.create_index(index_name, index_config)

    return ProductEventConsumer(
        kafka_client=kafka_client,
        consumer_name=consumer_group,
        enricher=enricher,
        indexer=indexer,
        index_name=index_name,
    )
