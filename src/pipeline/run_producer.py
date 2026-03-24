"""CLI entrypoint for publishing product events to Kafka."""

import argparse

from pipeline.pipeline import build_producer, load_events


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish product events to Kafka")
    parser.add_argument("--input", default="products.json", help="Path to the raw events JSON file")
    parser.add_argument("--topic", default="product-updates", help="Kafka topic name")
    parser.add_argument("--bootstrap-servers", default="localhost:9092", help="Kafka bootstrap servers")
    args = parser.parse_args()

    producer = build_producer(topic=args.topic, bootstrap_servers=args.bootstrap_servers)
    events = load_events(args.input)

    if not producer.kafka_client.health_check():
        raise ConnectionError(f"Kafka is not reachable at {args.bootstrap_servers}")

    for payload in events:
        producer.emit(payload)

    print(f"Published {len(events)} events to topic '{args.topic}'")


if __name__ == "__main__":
    main()

