from typing import Any, Dict

from pydantic import Field

from contextual.graph.components.repositories.crud_base import CRUDRepository
from contextual.graph.exceptions.components.repositories.mongodb_exceptions import (
    MongoDBCollectionNotFoundException,
)
from contextual.graph.models import FilterSchema, ModelSchemaExtractor

from .base_schema import SchemaExtractor


class SchemaExtractorMongoDB(SchemaExtractor):
    """Schema extractor implementation that retrieves extractor_schema definitions from a MongoDB repository.

    This class uses a CRUDRepository to fetch and construct structured extractor_schema objects
    for downstream data extraction tasks.
    """

    repository: CRUDRepository[Any, Any] = Field(
        ..., description="Repository for accessing extractor_schema definitions."
    )
    filters: FilterSchema = Field(
        ..., description="Filters to apply when extracting extractor_schema definitions."
    )

    async def extract(self, **kwargs: Dict[str, Any]) -> ModelSchemaExtractor:
        """Asynchronously extracts a extractor_schema object based on a extractor_schema identifier.

        Uses the repository to retrieve extractor_schema data and builds a `ModelSchemaExtractor` instance.

        Args:
            **kwargs (Dict[str, Any]): Additional parameters for extractor_schema extraction (currently unused).

        Returns:
            ModelSchemaExtractor: The structured extractor_schema extractor instance.

        Raises:
            MongoDBCollectionNotFound: The collection was not found in the database.
        """
        collection_filtered = await self.repository.async_read(filters=self.filters.model_dump())
        if collection_filtered is None or len(collection_filtered) == 0:
            raise MongoDBCollectionNotFoundException(
                "The collection was not found as the result list is empty."
            )
        result: Dict[str, Any] = collection_filtered[0]
        return ModelSchemaExtractor.create(id_schema=self.filters.id, raw_data=result)
