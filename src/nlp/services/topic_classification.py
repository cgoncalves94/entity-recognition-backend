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
