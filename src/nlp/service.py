import spacy
import torch
import torch.nn.functional as F

from bertopic import BERTopic
from scipy.spatial.distance import cosine
from spacy.matcher import Matcher
from transformers import AutoModel, AutoTokenizer

from src.nlp.config import nlp_config
from src.nlp.utils import load_json_file

# Load embeddings model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Load Spacy model for entity extraction
nlp = spacy.load("en_core_web_sm")


def load_tech_entities():
    """
    Load technology entities from a JSON file.
    """

    # Load the technology entities from the JSON file
    tech_entities = nlp_config.CORPUS_DIR

    return load_json_file(tech_entities)

def load_blueprints_corpus():
    """
    Load the blueprints corpus from a JSON file.
    """

    # Load the blueprints corpus from the JSON file
    blueprints_corpus = nlp_config.BLUEPRINTS_DIR

    return load_json_file(blueprints_corpus)


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

def mean_pooling(model_output, attention_mask):
    """
    Apply mean pooling to get the sentence embedding
    
    Parameters:
        model_output: The model's output.
        attention_mask: The attention mask to exclude padding tokens from the averaging process.
        
    Returns:
        torch.Tensor: The sentence embedding.
    """
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask


def get_embedding(text):
    """
    Get the embedding representation of the given text.

    Parameters:
        text (str): The input text to be embedded.

    Returns:
        torch.Tensor: The embedding representation of the text.
    """
    # Tokenize the input text and prepare it for the model
    inputs = tokenizer(
        text, return_tensors="pt", padding=True, truncation=True, max_length=512
    )
    # Generate the embeddings by passing the inputs to the model
    with torch.no_grad():  # Disable gradient computation
        outputs = model(**inputs)
    # Extract the embeddings from the model's output, which is the mean of the last hidden state
    embeddings = mean_pooling(outputs, inputs['attention_mask'])
    
    # Normalize the embeddings
    normalized_embeddings = F.normalize(embeddings, p=2, dim=1)
    
    # Return the embeddings after removing the batch dimension
    return normalized_embeddings.squeeze()


def cosine_similarity(a, b):
    """
    Calculates the cosine similarity between two vectors.

    Parameters:
        a (numpy.ndarray): The first vector.
        b (numpy.ndarray): The second vector.

    Returns:
        float: The cosine similarity between the two vectors.
    """
    # Calculate the cosine similarity, which is 1 minus the cosine distance
    return 1 - cosine(a.detach().numpy(), b.detach().numpy())


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


async def load_bertopic_model(model_object_name):
    """
    Load a BERTopic model from a given object name.

    Parameters:
        model_object_name (str): The name of the model object to load.

    Returns:
        BERTopic: The loaded BERTopic model.
    """

    topic_model = BERTopic.load(model_object_name)

    return topic_model


def classify_text(text, topic_model, topic_name_mapping):
    """
    Classifies the given text into a topic using the provided topic model.

    Parameters:
        text (str): The text to be classified.
        topic_model (BERTopic): The topic model used for classification.
        topic_name_mapping (dict): A dictionary mapping topic IDs to topic names.

    Returns:
        tuple: A tuple containing the predicted topic name and a list of keywords associated with the predicted topic.
    """
    # Use the topic model to predict the topic for the given text
    # The transform method returns a tuple with the predicted topic(s) and their probabilities
    predicted_topic, _ = topic_model.transform([text])

    # Retrieve the topic name using the predicted topic ID. If the ID is not found,
    # default to "Unknown Topic"
    topic_name = topic_name_mapping.get(predicted_topic[0], "Unknown Topic")

    # Get the list of keywords for the predicted topic. The get_topic method returns
    # a list of tuples with keywords and their relevance scores, but we only need the keywords
    keywords = [word for word, _ in topic_model.get_topic(predicted_topic[0])]

    # Return the predicted topic name and the associated keywords
    return topic_name, keywords


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
    explicit_mentions = [
        entity_dict["entity"]
        for entity_dict in entities
        if entity_dict["entity"].lower() in user_input.lower()
    ]

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
        relevance_score = sum(
            cosine_similarity(get_embedding(keyword), entity_embedding)
            for keyword in topic_keywords
        ) / len(topic_keywords)

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
        normalized_scores = {
            entity_name: score / max_score
            for entity_name, score in entities_scores.items()
        }
        # Sort the entities by their normalized scores in descending order.
        sorted_entities = sorted(
            normalized_scores.items(), key=lambda x: x[1], reverse=True
        )
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
        if (
            category not in best_entity_per_category
            or best_entity_per_category[category]["score"] < entity["score"]
        ):
            best_entity_per_category[category] = entity

    # Prepare recommendations based on the best entity for each category
    recommendations = [
        {"category": category, "recommendation": entity["entity_name"]}
        for category, entity in best_entity_per_category.items()
    ]

    return recommendations

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

    # Function to calculate match score based on blueprint tags
    def calculate_match_score(blueprint_tags):
        return len(blueprint_tags.intersection(all_matching_criteria))

    # Function to find the best match within a category or among nested blueprints
    def find_best_match(blueprints):
        best_match = None
        highest_score = 0
        for blueprint in blueprints:
            match_score = calculate_match_score(set(blueprint["tags"]))
            # Ensure all blueprint tags are covered by the matching criteria
            if match_score == len(blueprint["tags"]) and match_score > highest_score:
                best_match = blueprint
                highest_score = match_score
        return best_match

    for category in blueprints_corpus:
        # If the category has nested blueprints, evaluate those
        if "blueprints" in category:
            best_match = find_best_match(category["blueprints"])
            if best_match:
                matched_blueprints.setdefault(category["type"], []).append({
                    "name": best_match["name"],
                    "path": best_match["path"],
                    "description": best_match["description"],
                    "matched_tags": best_match["tags"]
                })
        else:
            # If it's a standalone blueprint, evaluate it directly
            best_match = find_best_match([category])
            if best_match:
                matched_blueprints.setdefault(category["type"], []).append({
                    "name": best_match["name"],
                    "path": best_match["path"],
                    "description": best_match["description"],
                    "matched_tags": best_match["tags"]
                })

    return matched_blueprints
