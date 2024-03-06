import joblib
import json
import base64
from google.oauth2.service_account import Credentials
from google.cloud import storage
from io import BytesIO

from transformers import AutoTokenizer, AutoModel

import spacy
from spacy.matcher import Matcher

from nlp.utils import load_json_file
from nlp.config import nlp_config

from scipy.spatial.distance import cosine

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

async def initialize_matcher_with_patterns(tech_entities):
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

def get_embedding(text):
    """
    Get the embedding representation of the given text.

    Parameters:
        text (str): The input text to be embedded.

    Returns:
        torch.Tensor: The embedding representation of the text.
    """
    # Tokenize the input text and prepare it for the model
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    # Generate the embeddings by passing the inputs to the model
    outputs = model(**inputs)
    # Extract the embeddings from the model's output, which is the mean of the last hidden state
    embeddings = outputs.last_hidden_state.mean(1)
    # Return the embeddings after removing the batch dimension
    return embeddings.squeeze()

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
            "type": entity_details['type'],
            "category": entity_details['category'],
            "description": entity_details['description'],
            "score": entity_details['score']
        }
        # Append the entity's details to the list of unique entities
        entities.append(extracted_entity)
        
    # Return the list of entities 
    return entities



async def load_bertopic_model_from_gcs(bucket_name, model_object_name):
    """
    Load a BERTopic model directly from Google Cloud Storage into memory without saving it locally.
    """

    # Decode the base64-encoded Google Cloud Service Account credentials
    sa_key_base64 = nlp_config.GCP_SA_KEY_BASE64
    sa_key_info = json.loads(base64.b64decode(sa_key_base64).decode('utf-8'))

    # Authenticate with Google Cloud Storage using the decoded credentials
    credentials = Credentials.from_service_account_info(sa_key_info)
    storage_client = storage.Client(credentials=credentials, project=sa_key_info['project_id'])

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(model_object_name)

    # Download the blob to an in-memory byte stream
    byte_stream = BytesIO()
    blob.download_to_file(byte_stream)
    byte_stream.seek(0)  # Seek to the start of the stream

    # Load the BERTopic model from the byte stream
    topic_model = joblib.load(byte_stream)

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
    explicit_mentions = [entity_dict['entity'] for entity_dict in entities if entity_dict['entity'].lower() in user_input.lower()]

    # Prepare a list of entities to be scored. If an entity has related technologies,
    # add those to the list instead of the entity itself.
    updated_entities = []
    for entity_dict in entities:
        entity_name = entity_dict['entity']
        if 'relatedTechnologies' in tech_entities.get(entity_name, {}):
            updated_entities.extend(tech_entities[entity_name]['relatedTechnologies'])
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

    return [{"entity_name": entity_name, "score": score, "category": category} 
        for category, entities_scores in sorted_entities_by_category.items() 
        for entity_name, score in entities_scores]

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
    recommendations = [{"category": category, "recommendation": entity["entity_name"]} 
                    for category, entity in best_entity_per_category.items()]

    return recommendations
