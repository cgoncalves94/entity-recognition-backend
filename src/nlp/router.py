from typing import List

from fastapi import APIRouter, Depends, FastAPI

from src.auth.jwt import parse_jwt_user_data
from src.auth.schemas import JWTData
from src.nlp.schemas import InputText, Recommendation
from src.nlp.service import (
    classify_text,
    dynamic_score_entities,
    extract_tech_entities,
    initialize_matcher_with_patterns,
    load_tech_entities,
    recommend_technologies,
)

router = APIRouter()


# Function to access the global FastAPI application instance
def get_application() -> FastAPI:
    from src.main import app

    return app


# Define a route to process input texts and return recommendations
@router.post("/process/", response_model=List[Recommendation])
async def process_texts(
    input_text: InputText,
    jwt_data: JWTData = Depends(parse_jwt_user_data),
    app: FastAPI = Depends(
        get_application
    ),  # Add dependency to access the app instance
):
    """
    Process a list of input texts and return recommendations based on extracted entities and predicted topics.

    Args:
      input_text (InputText): Input text data.
      jwt_data (JWTData, optional): JWT data. Defaults to Depends(parse_jwt_user_data).

    Returns:
      List[Recommendation]: List of recommendations for each input text.
    """
    tech_entities = (
        await load_tech_entities()
    )  # Load technology entities from a JSON file
    matcher = initialize_matcher_with_patterns(
        tech_entities
    )  # Initialize a spaCy Matcher object with patterns for tech entities

    # Access the preloaded BERTopic model from the app state
    topic_model = app.state.bertopic_model

    topic_info = (
        topic_model.get_topic_info()
    )  # Get information about the topics in the BERTopic model
    topic_name_mapping = dict(
        zip(topic_info["Topic"], topic_info["Name"])
    )  # Create a mapping of topic IDs to topic names
    results = []  # Initialize an empty list to store the results

    # Iterate over each input text
    for text in input_text.texts:
        extracted_entities = extract_tech_entities(
            text, tech_entities, matcher
        )  # Extract technology entities from the text
        entity_names = [
            entity["category"] for entity in extracted_entities
        ]  # Get the names of the extracted entities
        entity_string = ", ".join(
            entity_names
        )  # Create a string representation of the extracted entities
        text_to_classify = (
            text + ". " + entity_string
        )  # Concatenate the text and the entity string
        topic_name, topic_keywords = classify_text(
            text_to_classify, topic_model, topic_name_mapping
        )  # Classify the text into a topic using the BERTopic model
        sorted_entities = dynamic_score_entities(
            extracted_entities, topic_keywords, text, tech_entities
        )  # Score the entities based on their relevance to the text and topic keywords
        recommendations = recommend_technologies(
            sorted_entities
        )  # Recommend technologies based on the highest-scoring entity for each category

        # Append the results to the list
        results.append(
            {
                "input_text": text,
                "predicted_topic_name": topic_name,
                "extracted_entities": sorted_entities,
                "recommendations": recommendations,
            }
        )

    return results  # Return the list of results
