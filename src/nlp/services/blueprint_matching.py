from collections import defaultdict

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
    - blueprints (list): A list of blueprints.
    - all_matching_criteria (set): A set of all matching criteria.
    Returns:
    - dict: The best matching blueprint.
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
    Matches the recommendations from NLP output with the blueprints in the blueprints_corpus.

    Args:
      - nlp_output (list): List of dictionaries containing NLP output, including recommendations and extracted entities.
      - blueprints_corpus (list): List of dictionaries representing the blueprints corpus.

    Returns:
      - list: A list of dictionaries representing the matched blueprints, with details such as name, path, description, and matched tags.
      - None: If no blueprint matches the provided recommendations.
    """

    # Extract the recommendations from the NLP output
    recommendations = set(rec["recommendation"] for rec in nlp_output[0]["recommendations"])

    # If there are no recommendations, return None
    if not recommendations:
        return None

    # Group the blueprints by category
    blueprints_by_category = defaultdict(list)
    for blueprint in blueprints_corpus:
        category = blueprint.get("type", "Other")  # Use "Other" as the default category
        blueprints_by_category[category].append(blueprint)

    # Initialize the list of matched blueprints
    matched_blueprints = []

    # Iterate over each category of blueprints
    for category, category_blueprints in blueprints_by_category.items():
        # Initialize the best match to None
        best_match = None
        # Initialize the maximum number of matched tags to 0
        max_matched_tags = 0
        # Initialize the minimum number of total tags to infinity
        min_total_tags = float("inf")

        # Iterate over each blueprint in the category
        for blueprint in category_blueprints:
            # Get the set of tags for the blueprint
            blueprint_tags = set(blueprint["tags"])
            # Get the set of matched tags between the blueprint and the recommendations
            matched_tags = blueprint_tags.intersection(recommendations)
            # Get the number of matched tags
            num_matched_tags = len(matched_tags)
            # Get the total number of tags in the blueprint
            num_total_tags = len(blueprint_tags)

            # Update the best match if the number of matched tags is greater than the maximum number of matched tags,
            # or if the number of matched tags is equal to the max number of matched tags and the total number of tags is less than the min number of total tags
            if num_matched_tags > max_matched_tags or (num_matched_tags == max_matched_tags and num_total_tags < min_total_tags):
                best_match = {
                    "name": blueprint["name"],
                    "path": blueprint["path"],
                    "description": blueprint["description"],
                    "matched_tags": list(matched_tags),
                }
                # Update the maximum number of matched tags
                max_matched_tags = num_matched_tags
                # Update the minimum number of total tags
                min_total_tags = num_total_tags

        # If there is a best match and the best match has at least one matched tag, add the best match to the list of matched blueprints
        if best_match and best_match["matched_tags"]:
            matched_blueprints.append(best_match)

    # Return the list of matched blueprints, or None if there are no matched blueprints
    return matched_blueprints if matched_blueprints else None
