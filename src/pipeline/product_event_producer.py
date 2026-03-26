from base.base_producer import BaseProducer
from base.models import Event, EventType, Product
from datetime import datetime
from clients.kafka_client import KafkaClient

class ProductEventProducer(BaseProducer):

    def __init__(self, kafka_client: KafkaClient, topic: str):
        self.kafka_client = kafka_client
        self.topic = topic

    def emit(self, payload: dict) -> Event:
        product = Product(
            product_id=payload["product_id"],
            name=payload["name"],
            category=payload["category"],
            price=payload["price"],
            locale=payload["locale"],
        )

        event = Event(
            event_id=payload["event_id"],
            event_type=EventType(payload["event_type"]),
            product=product,
            timestamp=datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00")),
        )

        self.kafka_client.send(self.topic, event)
        return event
