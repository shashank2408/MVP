"""Base contract for index mapping builders."""

from abc import ABC, abstractmethod


class BaseMappingBuilder(ABC):
    @abstractmethod
    def build(self) -> dict:
        """Build an index mapping body."""

