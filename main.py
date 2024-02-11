# Import necessary modules from the src directory
from src.entity_extraction import extract_tech_entities, initialize_matcher_with_patterns
from src.topic_classification import classify_text, load_bertopic_model
from src.dynamic_scoring import dynamic_score_entities
from src.recommendation import recommend_technologies
from src.utilities import load_json_file

def main():
    # Load the technology entities from a JSON file. This file contains patterns and information
    # about different technology-related entities.
    tech_entities = load_json_file("data/tech_entities.json")
    
    # Initialize a matcher with the loaded tech entities to be used for entity extraction.
    # The matcher will use the patterns defined in the tech_entities to identify technology-related entities in the text.
    matcher = initialize_matcher_with_patterns(tech_entities)
    
    # Define the directory where the BERTopic model is stored.
    model_dir = "models/bertopic_model_entity"
    
    # Load the BERTopic model from the specified directory.
    # The BERTopic model is used to classify the text into a topic.
    topic_model = load_bertopic_model(model_dir)
    
    # Retrieve information about the topics from the model, including topic IDs and names.
    topic_info = topic_model.get_topic_info()
    
    # Create a mapping from topic IDs to topic names for easy lookup.
    topic_name_mapping = dict(zip(topic_info['Topic'], topic_info['Name']))

    # Define example input texts to be processed.
    # These texts will be processed one by one, and for each text, technology-related entities will be extracted,
    # the text will be classified into a topic, and the entities will be scored based on their relevance to the text and the topic.
    input_text = [
        "In comparing database management systems for our relational database architecture, we're evaluating the performance and features of MySQL versus MongoDB to determine the best fit for our SQL-based transactions.",
        "For our scalable web application, we're considering NoSQL databases to handle dynamic schemas and large data volumes, debating between MongoDB and MySQL for their flexibility and scalability."
    ]
    
    input_text2 = [
      "We need a user-friendly UI with a responsive design for our frontend.",
      "The backend should use a REST API and connect to a relational SQL database.",
      "Our application must be scalable and deployable on AWS infrastructure.",
      "We also need the appropriate GitHub repository and Implement CI/CD pipelines in GitHub."
    ]
    
    # Initialize a set to keep track of entities that have already been extracted.
    # This is used to avoid extracting the same entity multiple times from the same text.
    already_extracted = set()
    
    # Process each text in the input_text list.
    for text in input_text2:
        # Extract technology-related entities from the text using the matcher and the list of
        # already extracted entities to avoid duplicates.
        extracted_entities, already_extracted = extract_tech_entities(text, tech_entities, matcher, already_extracted)
        
        # Get the category of each extracted entity and join them into a string.
        # This string will be appended to the original text to provide additional context for topic classification.
        entity_names = [entity['category'] for entity in extracted_entities]
        entity_string = ', '.join(entity_names)
        
        # Append the entity string to the original text.
        text_to_classify = text + ". " + entity_string

        # Classify the text into a topic using the BERTopic model and the mapping of topic names.
        topic_name, topic_keywords = classify_text(text_to_classify, topic_model, topic_name_mapping)

        # Dynamically score the extracted entities based on their relevance to the text and the topic keywords.
        # The scoring is done by comparing the embeddings of the entities and the text.
        sorted_entities = dynamic_score_entities(extracted_entities, topic_keywords, text, tech_entities)

        # Print the results: the original text, the predicted topic name, and the sorted list of entities.
        print("\n")
        print(f"Input Text: {text}")
        print(f"Predicted Topic Name: {topic_name}")
        print(f"Extracted Entities: {sorted_entities}")
        
        # Generate recommendations based on the sorted entities.
        # The recommendations are the highest-scoring entities for each category.
        recommendations = recommend_technologies(sorted_entities)
        print("Recommendations:", recommendations)

# Check if the script is being run directly (as opposed to being imported) and, if so, execute the main function.
if __name__ == "__main__":
    main()