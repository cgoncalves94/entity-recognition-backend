from .embeddings import get_embedding
from .similarity import cosine_similarity

def dynamic_score_entities(entities, topic_keywords, user_input):
  """
  Calculates the dynamic scores for a list of entities based on their relevance to a user input and topic keywords.

  Args:
    entities (list): A list of dictionaries representing the entities.
      Each dictionary should have the following keys: 'entity', 'description', 'category', 'type', and 'score'.
    topic_keywords (list): A list of keywords related to the topic.
    user_input (str): The user input to compare the entities against.

  Returns:
    list: A sorted list of tuples, where each tuple contains an entity and its corresponding dynamic score.
      The list is sorted in descending order based on the dynamic scores.
  """
  # Generate an embedding for the user input text
  input_embedding = get_embedding(user_input)
  # Initialize a dictionary to hold the dynamic scores for each entity
  scores = {}
  # Loop through each entity to calculate its dynamic score
  for entity in entities:
    # Combine the entity's description, category, and type into a single string
    entity_text = f"{entity['description']} {entity['category']} {entity['type']}"
    # Generate an embedding for the combined entity text
    entity_embedding = get_embedding(entity_text)
    # Calculate the similarity score between the user input and the entity
    similarity = cosine_similarity(input_embedding, entity_embedding)
    # Calculate the average relevance score of the entity with respect to the topic keywords
    relevance_score = sum(cosine_similarity(get_embedding(keyword), entity_embedding) for keyword in topic_keywords) / len(topic_keywords)
    # Combine the static score with the similarity and relevance scores
    combined_score = entity['score'] + similarity + relevance_score
    # Store the combined score in the scores dictionary
    scores[entity['entity']] = combined_score
  # Normalize the scores by dividing by the maximum score to keep them in a range of 0 to 1
  max_score = max(scores.values(), default=1)
  normalized_scores = {entity: score / max_score for entity, score in scores.items()}
  # Sort the entities by their normalized scores in descending order
  sorted_entities = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
  # Return the sorted list of entities and their normalized scores
  return sorted_entities
