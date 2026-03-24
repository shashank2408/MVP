from abc import ABC, abstractmethod
from base.models import Event


class BaseProducer(ABC):
    @abstractmethod
    def emit(self, payload: dict) -> Event:
        """Build and publish an event from the input payload."""
