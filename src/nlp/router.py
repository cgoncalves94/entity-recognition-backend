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
    load_blueprints_corpus,
    load_tech_entities,
    match_blueprints,
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
    tech_entities = (
        await load_tech_entities()
    )  # Load technology entities from a JSON file
    
    blueprint_corpus = (
        await load_blueprints_corpus()
    ) # Load blueprint corpus from a JSON file
    
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
        # After generating recommendations
        recommendations = recommend_technologies(sorted_entities)

        # Now, prepare the data structure expected by match_blueprints
        nlp_output_for_matching = [{
            "input_text": text,
            "predicted_topic_name": topic_name,
            "extracted_entities": sorted_entities,
            "recommendations": recommendations  # Use the finalized recommendations
        }]
        
        # Call match_blueprints with the finalized NLP output
        matched_blueprints_dict = match_blueprints(nlp_output_for_matching, blueprint_corpus)

        # Assuming matched_blueprints_dict is obtained
        # Flatten the matched blueprints into a list
        matched_blueprints_list = []
        for category, blueprints in matched_blueprints_dict.items():
            for blueprint in blueprints:
                # Optionally, you could add the 'category' to the blueprint dict if needed
                # blueprint['category'] = category
                matched_blueprints_list.append(blueprint)

        # Append the results to the list, including matched blueprints
        results.append({
            "input_text": text,
            "predicted_topic_name": topic_name,
            "extracted_entities": sorted_entities,
            "recommendations": recommendations,
            "matched_blueprints": matched_blueprints_list  # This now matches the expected schema
        })

        # After processing all input texts
        return results
