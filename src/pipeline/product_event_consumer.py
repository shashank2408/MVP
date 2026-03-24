from base.base_consumer import BaseConsumer
from base.base_enricher import BaseEnricher
from base.base_indexer import BaseIndexer
from base.models import Event
from clients.kafka_client import KafkaClient


class ProductEventConsumer(BaseConsumer):

    def __init__(self,
                kafka_client: KafkaClient,
                consumer_name: str,
                enricher: BaseEnricher,
                indexer: BaseIndexer,
                index_name: str):
        self.kafka_client = kafka_client
        self.consumer_name = consumer_name
        self.enricher = enricher
        self.indexer = indexer
        self.index_name = index_name

    def consume(self, event: Event) -> None:
        enriched_product = self.enricher.enrich(event.product)
        self.indexer.index_document(
            index_name=self.index_name,
            document=enriched_product,
            document_id=enriched_product.product_id,
        )

    def run(self, timeout_ms: int = 1000) -> None:
        events = self.kafka_client.poll(timeout_ms=timeout_ms)
        for event in events:
            self.consume(event)
