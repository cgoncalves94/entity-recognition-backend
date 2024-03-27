from spacy.matcher import Matcher

from src.nlp.config import nlp_config
from src.nlp.models import load_spacy_model
from src.nlp.utils import load_json_file

nlp = load_spacy_model()


def load_tech_entities():
    """
    Load technology entities from a JSON file.
    """

    # Load the technology entities from the JSON file
    tech_entities = nlp_config.CORPUS_DIR

    return load_json_file(tech_entities)


def initialize_matcher_with_patterns(tech_entities):
    """
    Initialize a spaCy Matcher object with patterns for tech entities.

    Args:
        tech_entities (dict): A dictionary containing tech entity names as keys and their patterns as values.

    Returns:
        Matcher: A spaCy Matcher object initialized with the provided patterns.
    """
    matcher = Matcher(nlp.vocab)
    for name, entity in tech_entities.items():
        # Assuming entity["patterns"] is a list of pattern dictionaries
        patterns = entity["patterns"]
        # Define patterns for the matcher to identify tech entities in text
        matcher.add(name, patterns)
    # Return the matcher with all the added patterns
    return matcher


def extract_tech_entities(text, tech_entities, matcher):
    """
    Extracts technology entities from the given text using a spaCy matcher.

    Args:
        text (str): The input text from which to extract entities.
        tech_entities (dict): A dictionary containing information about the technology entities.
        matcher (spacy.matcher.Matcher): The spaCy matcher object used for entity matching.

    Returns:
        list: A list of dictionaries containing information about the extracted entities.
    """

    # Process the text with the spaCy NLP pipeline to create a document object
    doc = nlp(text)
    # Use the matcher to find all matches in the document
    matches = matcher(doc)
    # Initialize a list to store entities found in the text
    entities = []
    # Iterate over each match to extract the entity details
    for match_id, start, end in matches:
        # Retrieve the string representation of the entity's match ID
        entity_key = nlp.vocab.strings[match_id]
        # Access the entity's details from the tech_entities dictionary using the entity_key
        entity_details = tech_entities[entity_key]
        # Create a dictionary with the entity's details
        extracted_entity = {
            "entity": entity_key,
            "type": entity_details["type"],
            "category": entity_details["category"],
            "description": entity_details["description"],
            "score": entity_details["score"],
        }
        # Append the entity's details to the list of unique entities
        entities.append(extracted_entity)

    # Return the list of entities
    return entities
