from typing import Dict, List

from pydantic import BaseModel, Field


class InputText(BaseModel):
    """
    Represents the input text for entity recognition.
    """

    texts: List[str] = Field(..., json_schema_extra={"example": "Example Value"})


class Recommendation(BaseModel):
    """
    Represents the recommendation for the input text.
    """

    input_text: str
    predicted_topic_name: str
    extracted_entities: List[Dict]
    recommendations: List[Dict]
