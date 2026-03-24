from abc import ABC, abstractmethod
from base.models import Event

class BaseConsumer(ABC):

    @abstractmethod
    def consume(self, event: Event) -> None:
        pass
