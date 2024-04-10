from typing import Dict, List
from pydantic import BaseModel, Field

class InputText(BaseModel):
    """ Represents the input text for entity recognition. """
    texts: List[str] = Field(..., json_schema_extra={"example": ["Example Value"]})

class Recommendation(BaseModel):
    """Represents the recommendation for the input text."""
    input_text: str = Field(..., json_schema_extra={"example": "Example text"})
    predicted_topic_name: str = Field(..., json_schema_extra={"example": "Example topic name"})
    extracted_entities: List[Dict] = Field(..., json_schema_extra={"example": [{"entity_name": "Example", "score": 1, "category": "Example Category"}]})
    recommendations: List[Dict] = Field(..., json_schema_extra={"example": [{"category": "Example Category", "recommendation": "Example Recommendation"}]})

class BlueprintMatch(BaseModel):
    """Represents the blueprint match for the input text."""
    matched_blueprints: List[Dict] = Field(..., json_schema_extra={"example": [{"blueprint_name": "Example Blueprint"}]})
