from typing import List

from fastapi import APIRouter, Depends, FastAPI

from src.auth.jwt import parse_jwt_user_data
from src.auth.schemas import JWTData
from src.nlp.schemas import BlueprintMatch, InputText, Recommendation
from src.nlp.services.blueprint_matching import load_blueprints_corpus, match_blueprints
from src.nlp.services.entity_extraction import (
    extract_tech_entities,
    initialize_matcher_with_patterns,
    load_tech_entities,
)
from src.nlp.services.recommendation_generation import dynamic_score_entities, recommend_technologies
from src.nlp.services.topic_classification import classify_text

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
    app: FastAPI = Depends(get_application),  
):
    """
    Process a list of input texts and generate recommendations based on extracted entities and topic classification.

    This endpoint takes a list of input texts, extracts technology entities from each text, classifies the texts into topics
    using a pre-trained BERTopic model, and generates recommendations based on the extracted entities and their relevance to
    the identified topics.

    Parameters:
    - input_text : The input texts to process.
    - jwt_data: JWT data of the authenticated user.
    - app: The FastAPI application instance. 

    Returns:
    - A list of Recommendation objects containing the processed results for each input text. 
    Each Recommendation object includes the input text, predicted topic name, extracted entities, and generated recommendations.
    """

    tech_entities = await load_tech_entities()  # Load technology entities from a JSON file

    matcher = initialize_matcher_with_patterns(tech_entities)  # Initialize a spaCy Matcher object with patterns for tech entities

    # Access the preloaded BERTopic model from the app state
    topic_model = app.state.bertopic_model

    topic_info = topic_model.get_topic_info()  # Get information about the topics in the BERTopic model
    topic_name_mapping = dict(zip(topic_info["Topic"], topic_info["Name"]))  # Create a mapping of topic IDs to topic names
    results = []  # Initialize an empty list to store the results

    # Iterate over each input text
    for text in input_text.texts:
        extracted_entities = extract_tech_entities(text, tech_entities, matcher)  # Extract technology entities from the text
        entity_names = [entity["category"] for entity in extracted_entities]  # Get the names of the extracted entities
        entity_string = ", ".join(entity_names)  # Create a string representation of the extracted entities
        text_to_classify = text + ". " + entity_string  # Concatenate the text and the entity string
        topic_name, topic_keywords = classify_text(text_to_classify, topic_model, topic_name_mapping)  # Classify the text into a topic using the BERTopic model
        sorted_entities = dynamic_score_entities(
            extracted_entities, topic_keywords, text, tech_entities
        )  # Score the entities based on their relevance to the text and topic keywords
        # After generating recommendations
        recommendations = recommend_technologies(sorted_entities)

        # Append the processed results to the list
        results.append({"input_text": text, "predicted_topic_name": topic_name, "extracted_entities": sorted_entities, "recommendations": recommendations})

    # After processing all input texts
    return results


# Define a route to match recommendations with blueprints
@router.post("/match-blueprints/", response_model=List[BlueprintMatch])
async def match_blueprint_endpoint(recommendations: List[Recommendation], jwt_data: JWTData = Depends(parse_jwt_user_data)):
    """
    Match the provided recommendations with blueprints in the blueprints corpus.

    This endpoint takes a list of recommendations and matches them with relevant blueprints from the blueprints corpus.
    It returns a list of BlueprintMatch objects containing the matched blueprints for each recommendation.

    Parameters:
    - A list of Recommendation objects to match with blueprints.
    - jwt_data: JWT data of the authenticated user.

    Returns:
    - A list of BlueprintMatch objects containing the matched blueprints for each recommendation.
    """

    blueprints_corpus = await load_blueprints_corpus()
    all_matched_blueprints = []

    for recommendation in recommendations:
      matched_blueprints = match_blueprints([recommendation.model_dump()], blueprints_corpus)
      if matched_blueprints:
        all_matched_blueprints.extend(matched_blueprints)

    return [BlueprintMatch(matched_blueprints=all_matched_blueprints)]  

