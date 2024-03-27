from src.nlp.config import nlp_config
from src.nlp.utils import load_json_file


def load_blueprints_corpus():
    """
    Load the blueprints corpus from a JSON file.
    """

    # Load the blueprints corpus from the JSON file
    blueprints_corpus = nlp_config.BLUEPRINTS_DIR

    return load_json_file(blueprints_corpus)


def calculate_match_score(blueprint_tags, all_matching_criteria):
    """
    Calculates the match score between the blueprint tags and all matching criteria.

    Parameters:
    - blueprint_tags (set): A set of tags from the blueprint.
    - all_matching_criteria (set): A set of all matching criteria.

    Returns:
    - match_score (int): The number of tags that match between the blueprint tags and all matching criteria.
    """
    return len(blueprint_tags.intersection(all_matching_criteria))


def find_best_match(blueprints, all_matching_criteria):
    """
    Finds the best match from a list of blueprints based on the matching criteria.

    Args:
      blueprints (list): A list of blueprints.
      all_matching_criteria (list): A list of matching criteria.

    Returns:
      dict: The best matching blueprint.

    """
    best_match = None
    highest_score = 0
    for blueprint in blueprints:
        match_score = calculate_match_score(set(blueprint["tags"]), all_matching_criteria)
        if match_score == len(blueprint["tags"]) and match_score > highest_score:
            best_match = blueprint
            highest_score = match_score
    return best_match


def match_blueprints(nlp_output, blueprints_corpus):
    """
    Matches the extracted entities and recommendations from NLP output with the blueprints in the blueprints_corpus.

    Args:
        nlp_output (list): List of dictionaries containing NLP output, including recommendations and extracted entities.
        blueprints_corpus (list): List of dictionaries representing the blueprints corpus.

    Returns:
        dict: A dictionary containing the matched blueprints categorized by type, with details such as name, path, description, and matched tags.
    """
    matched_blueprints = {}
    recommendations = set(rec["recommendation"] for rec in nlp_output[0]["recommendations"])
    extracted_entities = set(entity["entity_name"] for entity in nlp_output[0]["extracted_entities"])
    all_matching_criteria = recommendations.union(extracted_entities)

    for category in blueprints_corpus:
        if "blueprints" in category:
            best_match = find_best_match(category["blueprints"], all_matching_criteria)
        else:
            best_match = find_best_match([category], all_matching_criteria)

        if best_match:
            matched_blueprints.setdefault(category["type"], []).append(
                {
                    "name": best_match["name"],
                    "path": best_match["path"],
                    "description": best_match["description"],
                    "matched_tags": best_match["tags"],
                }
            )

    return matched_blueprints
