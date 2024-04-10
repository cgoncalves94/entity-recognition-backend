from typing import Dict, List
from pydantic import BaseModel, Field

class InputText(BaseModel):
    """ Represents the input text for entity recognition. """
    texts: List[str] = Field(..., example=["Example Value"])

class Recommendation(BaseModel):
    """ Represents the recommendation for the input text. """
    input_text: str = Field(..., example="Example text")
    predicted_topic_name: str = Field(..., example="Example topic name")
    extracted_entities: List[Dict] = Field(..., example=[{"entity_name": "Example", "score": 1, "category": "Example Category"}])
    recommendations: List[Dict] = Field(..., example=[{"category": "Example Category", "recommendation": "Example Recommendation"}])

class BlueprintMatch(BaseModel):
    """ Represents the blueprint match for the input text. """
    matched_blueprints: List[Dict] = Field(..., example=[{"blueprint_name": "Example Blueprint", "score": 0.8}])