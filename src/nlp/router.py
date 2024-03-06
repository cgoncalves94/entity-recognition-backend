from typing import List
from fastapi import APIRouter, Depends, FastAPI

from auth.jwt import parse_jwt_user_data
from auth.schemas import JWTData

from nlp.schemas import InputText, Recommendation
from nlp.service import (
  load_tech_entities,
  initialize_matcher_with_patterns,
  extract_tech_entities,
  classify_text,
  dynamic_score_entities,
  recommend_technologies,
)

router = APIRouter()

# Function to access the global FastAPI application instance
def get_application() -> FastAPI:
    from main import app  
    return app

# Define a route to process input texts and return recommendations
@router.post("/process/", response_model=List[Recommendation])
async def process_texts(
  input_text: InputText, 
  jwt_data: JWTData = Depends(parse_jwt_user_data),
  app: FastAPI = Depends(get_application)  # Add dependency to access the app instance
):
  """
  Process a list of input texts and return recommendations based on extracted entities and predicted topics.

  Args:
    input_text (InputText): Input text data.
    jwt_data (JWTData, optional): JWT data. Defaults to Depends(parse_jwt_user_data).

  Returns:
    List[Recommendation]: List of recommendations for each input text.
  """
  tech_entities = await load_tech_entities()
  matcher = await initialize_matcher_with_patterns(tech_entities)

  # Access the preloaded BERTopic model from the app state
  topic_model = app.state.bertopic_model

  topic_info = topic_model.get_topic_info()
  topic_name_mapping = dict(zip(topic_info['Topic'], topic_info['Name']))
  results = []

  for text in input_text.texts:
      extracted_entities = extract_tech_entities(text, tech_entities, matcher)
      entity_names = [entity['category'] for entity in extracted_entities]
      entity_string = ', '.join(entity_names)
      text_to_classify = text + ". " + entity_string
      topic_name, topic_keywords = classify_text(text_to_classify, topic_model, topic_name_mapping)
      sorted_entities = dynamic_score_entities(extracted_entities, topic_keywords, text, tech_entities)
      recommendations = recommend_technologies(sorted_entities)
      results.append({
        "input_text": text,
        "predicted_topic_name": topic_name,
        "extracted_entities": sorted_entities,
        "recommendations": recommendations
      })
  return results