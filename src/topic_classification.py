import os
from bertopic import BERTopic
import configparser


def load_bertopic_model(model_dir, model_name="bertopic_model_entity"):
  """
  Loads a BERTopic model from the specified directory.

  Parameters:
    model_dir (str): The directory where the model is stored.
    model_name (str): The name of the model file. Default is "bertopic_model_entity".

  Returns:
    BERTopic: The loaded BERTopic model.
  """
  
  # Create a new ConfigParser object
  config = configparser.ConfigParser()

  # Read the configuration from a file
  config.read('config.ini')

  # Get the default model name from the configuration
  default_model_name = config.get('DEFAULT', 'model_name')

  
  model_path = os.path.join(model_dir, model_name)
  if os.path.exists(model_path):
    # Load the model from the specified path if it exists
    topic_model = BERTopic.load(model_path)
  else:
    # Load from the internet a default model defined on config.ini if the specified model is not found
    topic_model = BERTopic.load(default_model_name)
    # Create the model directory if it does not exist
    if not os.path.exists(model_dir):
      os.makedirs(model_dir)
    # Save the downloaded model to the specified path
    topic_model.save(model_path)
  # Return the loaded or downloaded BERTopic model
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
