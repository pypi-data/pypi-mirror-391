"""State representation exchanged between graph nodes."""

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field


class State(BaseModel):
    """State.

    Immutable snapshot that links raw text, the extractor_schema used to parse it,
    and the structured data extracted with that extractor_schema.

    Attributes:
        text (str): The original text to process.
        model_schema (Type[BaseModel]): The extractor_schema model used to interpret the text.
        data_extracted (BaseModel): The structured data extracted from the text.
    """

    text: str = Field(..., description="The original text to process.")
    model_schema: Optional[BaseModel | Type[BaseModel]] = Field(
        ..., description="The extractor_schema model used to interpret the text."
    )

    data_extracted: BaseModel | None | Dict[Any, Any] = Field(
        None, description="The structured data extracted from the text."
    )
