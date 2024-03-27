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
    app: FastAPI = Depends(get_application),  # Add dependency to access the app instance
):
    """
    Process a list of input texts by extracting technology entities, classifying them into topics,
    scoring the entities based on relevance, generating recommendations, matching blueprints,
    and returning the results.

    Args:
        input_text (InputText): The input texts to process.
        jwt_data (JWTData, optional): The JWT data. Defaults to Depends(parse_jwt_user_data).
        app (FastAPI, optional): The FastAPI application instance. Defaults to Depends(get_application).

    Returns:
        List[Dict]: A list of dictionaries containing the processed results for each input text.
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
    Matches recommendations with blueprints and returns a list of matched blueprints.

    Args:
      recommendations (List[Recommendation]): A list of recommendations to be matched with blueprints.
      jwt_data (JWTData, optional): JWT data obtained from the request. Defaults to Depends(parse_jwt_user_data).

    Returns:
      List[BlueprintMatch]: A list of BlueprintMatch objects containing the matched blueprints.
    """

    blueprints_corpus = await load_blueprints_corpus()
    all_matched_blueprints = []

    for recommendation in recommendations:
        matched_blueprints = match_blueprints([recommendation.model_dump()], blueprints_corpus)

        # Construct BlueprintMatch correctly with the list of matched blueprints
        matched_blueprint_object = BlueprintMatch(matched_blueprints=[bp for _, bps in matched_blueprints.items() for bp in bps])

        all_matched_blueprints.append(matched_blueprint_object)

    return all_matched_blueprints
