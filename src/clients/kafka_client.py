"""Kafka client wrapper with uniform producer/consumer connection setup."""

from dataclasses import asdict
from datetime import datetime
from enum import Enum
import json

from base.base_client import BaseClient
from base.models import Event, EventType, Product
from kafka import KafkaConsumer, KafkaProducer


class KafkaClientType(str, Enum):
    PRODUCER = "producer"
    CONSUMER = "consumer"


class KafkaClient(BaseClient):
    def __init__(
        self,
        client_type: KafkaClientType,
        bootstrap_servers: str = "localhost:9092",
        topic: str | None = None,
        group_id: str = "product-search-group",
    ) -> None:
        self.client_type = client_type
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.client = None

    def connect(self) -> None:
        if self.client_type == KafkaClientType.PRODUCER:
            self.client = KafkaProducer(bootstrap_servers=self.bootstrap_servers)
            return

        if self.client_type == KafkaClientType.CONSUMER:
            if self.topic is None:
                raise ValueError("Kafka consumer requires a topic")
            self.client = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
            )
            return

        raise ValueError(f"Unsupported Kafka client type: {self.client_type}")

    def health_check(self) -> bool:
        try:
            if self.client is None:
                self.connect()
            return bool(self.client.bootstrap_connected())
        except Exception:
            return False

    def send(self, topic: str, event: Event) -> None:
        if self.client_type != KafkaClientType.PRODUCER:
            raise ValueError("send is only supported for producer clients")
        if self.client is None:
            self.connect()

        payload = json.dumps(self._serialize_event(event)).encode("utf-8")
        future = self.client.send(topic, payload)
        self.client.flush()
        future.get(timeout=10)

    def poll(self, timeout_ms: int = 1000) -> list[Event]:
        if self.client_type != KafkaClientType.CONSUMER:
            raise ValueError("poll is only supported for consumer clients")
        if self.client is None:
            self.connect()

        records = self.client.poll(timeout_ms=timeout_ms)
        events: list[Event] = []

        for topic_records in records.values():
            for record in topic_records:
                events.append(self._deserialize_event(record.value))

        return events

    def close(self) -> None:
        if self.client is not None:
            self.client.close()
            self.client = None

    def _serialize_event(self, event: Event) -> dict:
        payload = asdict(event)
        payload["event_type"] = event.event_type.value
        payload["timestamp"] = event.timestamp.isoformat()
        return payload

    def _deserialize_event(self, value: bytes) -> Event:
        payload = json.loads(value.decode("utf-8"))
        product_payload = payload["product"]
        product = Product(
            product_id=product_payload["product_id"],
            name=product_payload["name"],
            category=product_payload["category"],
            price=product_payload.get("price", 0.0),
            locale=product_payload.get("locale", "en-US"),
        )

        return Event(
            event_id=payload["event_id"],
            event_type=EventType(payload["event_type"]),
            product=product,
            timestamp=datetime.fromisoformat(payload["timestamp"]),
        )
