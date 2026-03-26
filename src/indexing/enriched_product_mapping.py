"""OpenSearch mapping builder derived from the EnrichedProduct model."""

from dataclasses import fields
from types import UnionType
from typing import get_args, get_origin

from base.models import EnrichedProduct, PopularitySignals
from base.base_mapping import BaseMappingBuilder


class EnrichedProductMappingBuilder(BaseMappingBuilder):
    SKIP_FIELDS = {"semantic_embedding"}

    FIELD_OVERRIDES = {
        "product_id": {"type": "keyword"},
        "category": {"type": "keyword"},
        "brand": {"type": "keyword"},
        "locale": {"type": "keyword"},
        "tags": {"type": "keyword"},
        "semantic_text": {"type": "text"},
    }

    def build(self) -> dict:
        properties: dict[str, dict] = {}

        for field_info in fields(EnrichedProduct):
            field_name = field_info.name
            if field_name in self.SKIP_FIELDS:
                continue
            if field_name in self.FIELD_OVERRIDES:
                properties[field_name] = self.FIELD_OVERRIDES[field_name]
                continue
            properties[field_name] = self._map_python_type(field_info.type)

        return {"mappings": {"properties": properties}}

    def _map_python_type(self, annotation: object) -> dict:
        if annotation is str:
            return {"type": "text"}

        if annotation is int:
            return {"type": "integer"}

        if annotation is float:
            return {"type": "float"}

        if annotation is PopularitySignals:
            return {
                "properties": {
                    "views": {"type": "integer"},
                    "carts": {"type": "integer"},
                    "sales": {"type": "integer"},
                    "returns": {"type": "integer"},
                }
            }

        origin = get_origin(annotation)
        if origin is list:
            item_type = get_args(annotation)[0]
            if item_type is str:
                return {"type": "text"}

        if isinstance(annotation, UnionType):
            non_none_types = [arg for arg in get_args(annotation) if arg is not type(None)]
            if non_none_types:
                return self._map_python_type(non_none_types[0])

        return {"type": "text"}
