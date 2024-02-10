# Import necessary modules from the src directory
from src.entity_extraction import extract_tech_entities, initialize_matcher_with_patterns
from src.topic_classification import classify_text, load_bertopic_model
from src.dynamic_scoring import dynamic_score_entities
from src.utilities import load_json_file

def main():
    # Load the technology entities from a JSON file. This file contains patterns and information
    # about different technology-related entities.
    tech_entities = load_json_file("data/tech_entities.json")
    
    # Initialize a matcher with the loaded tech entities to be used for entity extraction.
    matcher = initialize_matcher_with_patterns(tech_entities)
    
    # Define the directory where the BERTopic model is stored.
    model_dir = "models/bertopic_model_entity"
    
    # Load the BERTopic model from the specified directory.
    topic_model = load_bertopic_model(model_dir)
    
    # Retrieve information about the topics from the model, including topic IDs and names.
    topic_info = topic_model.get_topic_info()
    
    # Create a mapping from topic IDs to topic names for easy lookup.
    topic_name_mapping = dict(zip(topic_info['Topic'], topic_info['Name']))

    # Define example input texts to be processed.
    input_text = [
        "In comparing database management systems for our relational database architecture, we're evaluating the performance and features of MySQL versus MongoDB to determine the best fit for our SQL-based transactions.",
        "For our scalable web application, we're considering NoSQL databases to handle dynamic schemas and large data volumes, debating between MongoDB and MySQL for their flexibility and scalability."
    ]
    
    # Initialize a set to keep track of entities that have already been extracted.
    already_extracted = set()
    
    # Process each text in the input_text list.
    for text in input_text:
        # Extract technology-related entities from the text using the matcher and the list of
        # already extracted entities to avoid duplicates.
        extracted_entities, already_extracted = extract_tech_entities(text, tech_entities, matcher, already_extracted)

        # Classify the text into a topic using the BERTopic model and the mapping of topic names.
        topic_name, topic_keywords = classify_text(text, topic_model, topic_name_mapping)

        # Dynamically score the extracted entities based on their relevance to the text and the topic keywords.
        sorted_entities = dynamic_score_entities(extracted_entities, topic_keywords, text)

        # Print the results: the original text, the predicted topic name, and the sorted list of entities.
        print(f"Input Text: {text}")
        print(f"Predicted Topic Name: {topic_name}")
        print(f"Sorted Entities: {sorted_entities}")

# Check if the script is being run directly (as opposed to being imported) and, if so, execute the main function.
if __name__ == "__main__":
    main()