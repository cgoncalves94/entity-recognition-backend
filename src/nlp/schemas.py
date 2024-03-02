from pydantic import BaseModel, Field
from typing import List, Dict

class InputText(BaseModel):
    texts: List[str] = Field(..., example=["Your example text here."])

class Recommendation(BaseModel):
    input_text: str
    predicted_topic_name: str
    extracted_entities: List[Dict]
    recommendations: List[Dict]
    
    