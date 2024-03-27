import spacy
from bertopic import BERTopic
from transformers import AutoModel, AutoTokenizer


async def load_embeddings_model():
    """
    Loads the embeddings model for sentence transformation.

    Returns:
      tokenizer (AutoTokenizer): The tokenizer for the embeddings model.
      model (AutoModel): The embeddings model.
    """
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    return tokenizer, model


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


def load_spacy_model():
    """
    Loads the Spacy model for English language.

    Returns:
      nlp (spacy.Language): The loaded Spacy model.
    """
    nlp = spacy.load("en_core_web_sm")
    return nlp
