from src.nlp.utils import cosine_similarity, get_embedding


def dynamic_score_entities(entities, topic_keywords, user_input, tech_entities):
    """
    Scores the entities based on their relevance to the user input and topic keywords.

    Args:
        entities (list): List of entity dictionaries.
        topic_keywords (list): List of topic keywords.
        user_input (str): User input text.
        tech_entities (dict): Dictionary of tech entities.

    Returns:
        dict: Sorted entities by category with their combined scores.
    """

    # Get the embedding of the user input. This will be used to calculate the similarity
    # between the user input and each entity.
    input_embedding = get_embedding(user_input)
    scores = {}

    # Identify explicit mentions of entities in the user input.
    explicit_mentions = [entity_dict["entity"] for entity_dict in entities if entity_dict["entity"].lower() in user_input.lower()]

    # Prepare a list of entities to be scored. If an entity has related technologies,
    # add those to the list instead of the entity itself.
    updated_entities = []
    for entity_dict in entities:
        entity_name = entity_dict["entity"]
        if "relatedTechnologies" in tech_entities.get(entity_name, {}):
            updated_entities.extend(tech_entities[entity_name]["relatedTechnologies"])
        else:
            updated_entities.append(entity_name)

    # Score entities, applying a boost for explicit mentions
    for entity_name in updated_entities:
        # Get the information about the entity from the tech_entities dictionary.
        entity_info = tech_entities.get(entity_name, {})
        # Prepare the text that represents the entity. This includes the entity's description,
        # category, and type.
        entity_text = f"{entity_info.get('description', '')} {entity_info.get('category', '')} {entity_info.get('type', '')}"
        # Get the embedding of the entity text.
        entity_embedding = get_embedding(entity_text)
        # Calculate the cosine similarity between the user input and the entity.
        similarity = cosine_similarity(input_embedding, entity_embedding)
        # Calculate the relevance score of the entity based on its similarity to the topic keywords.
        relevance_score = sum(cosine_similarity(get_embedding(keyword), entity_embedding) for keyword in topic_keywords) / len(topic_keywords)

        # The combined score is the sum of the similarity and the relevance score.
        combined_score = similarity + relevance_score

        # Apply a scoring boost for explicit mentions of the entity in the user input.
        if entity_name in explicit_mentions:
            combined_score += 0.2  # Adjust this boost value as needed

        # Get the category of the entity. If the entity doesn't have a category, use "Uncategorized".
        category = entity_info.get("category", "Uncategorized")
        # If this is the first entity of this category, initialize a new dictionary for the category.
        if category not in scores:
            scores[category] = {}
        # Add the entity and its score to the category's dictionary.
        scores[category][entity_name] = combined_score

    # Normalize and sort scores within each category
    sorted_entities_by_category = {}
    for category, entities_scores in scores.items():
        # Get the maximum score in the category.
        max_score = max(entities_scores.values(), default=1)
        # Normalize the scores by dividing each score by the maximum score.
        normalized_scores = {entity_name: score / max_score for entity_name, score in entities_scores.items()}
        # Sort the entities by their normalized scores in descending order.
        sorted_entities = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        # Add the sorted entities to the sorted_entities_by_category dictionary.
        sorted_entities_by_category[category] = sorted_entities

    return [
        {"entity_name": entity_name, "score": score, "category": category}
        for category, entities_scores in sorted_entities_by_category.items()
        for entity_name, score in entities_scores
    ]


def recommend_technologies(entities):
    """
    Recommends technologies based on the highest-scoring entity for each category.

    Args:
        entities (list): A list of dictionaries containing sorted entities by category.

    Returns:
        list: A list of dictionaries containing recommendations for each category.
    """
    # Initialize a dictionary to hold the highest-scoring entity for each category
    best_entity_per_category = {}

    # Iterate through entities to find the highest-scoring entity for each category
    for entity in entities:
        category = entity["category"]
        if category not in best_entity_per_category or best_entity_per_category[category]["score"] < entity["score"]:
            best_entity_per_category[category] = entity

    # Prepare recommendations based on the best entity for each category
    recommendations = [{"category": category, "recommendation": entity["entity_name"]} for category, entity in best_entity_per_category.items()]

    return recommendations
