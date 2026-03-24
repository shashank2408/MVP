"""CLI entrypoint for consuming product events from Kafka and indexing them."""

import argparse

from pipeline.pipeline import build_consumer


def main() -> None:
    parser = argparse.ArgumentParser(description="Consume product events from Kafka")
    parser.add_argument("--topic", default="product-updates", help="Kafka topic name")
    parser.add_argument("--bootstrap-servers", default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--consumer-group", default="product-search-indexer-group", help="Kafka consumer group")
    parser.add_argument("--tags", default="tags.json", help="Path to the tags JSON file")
    parser.add_argument("--index", default="products", help="OpenSearch index name")
    parser.add_argument("--opensearch-host", default="localhost", help="OpenSearch host")
    parser.add_argument("--opensearch-port", type=int, default=9200, help="OpenSearch port")
    parser.add_argument("--timeout-ms", type=int, default=1000, help="Kafka poll timeout in milliseconds")
    parser.add_argument("--once", action="store_true", help="Consume a single poll batch and exit")
    args = parser.parse_args()

    consumer = build_consumer(
        topic=args.topic,
        bootstrap_servers=args.bootstrap_servers,
        consumer_group=args.consumer_group,
        tags_path=args.tags,
        index_name=args.index,
        opensearch_host=args.opensearch_host,
        opensearch_port=args.opensearch_port,
    )

    if not consumer.kafka_client.health_check():
        raise ConnectionError(f"Kafka is not reachable at {args.bootstrap_servers}")

    if args.once:
        consumer.run(timeout_ms=args.timeout_ms)
        return

    try:
        while True:
            consumer.run(timeout_ms=args.timeout_ms)
    except KeyboardInterrupt:
        consumer.kafka_client.close()


if __name__ == "__main__":
    main()
