"""Base client contract for external systems."""

from abc import ABC, abstractmethod


class BaseClient(ABC):
    @abstractmethod
    def connect(self) -> None:
        """Initialize the underlying client connection."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return True when the external system is reachable."""

    @abstractmethod
    def close(self) -> None:
        """Release client resources."""

