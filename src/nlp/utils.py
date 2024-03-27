import json
import os

import aiofiles
import torch
import torch.nn.functional as F
from fastapi import FastAPI
from scipy.spatial.distance import cosine


# Function to access the global FastAPI application instance
def get_application() -> FastAPI:
    from src.main import app

    return app


async def load_json_file(file_path):
    # Detailed explanation of the function's purpose
    """
    Load a JSON file from the given file path.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The contents of the JSON file as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.

    """
    # Check if the file exists at the given path
    if os.path.exists(file_path):
        async with aiofiles.open(file_path, mode="r") as file:
            # Load the JSON content from the file and return it as a dictionary
            return json.loads(await file.read())
    else:
        # Raise an error if the file does not exist
        raise FileNotFoundError(f"File not found: {file_path}")


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
    app = get_application()
    tokenizer = app.state.tokenizer
    model = app.state.model

    # Tokenize the input text and prepare it for the model
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    # Generate the embeddings by passing the inputs to the model
    with torch.no_grad():  # Disable gradient computation
        outputs = model(**inputs)
    # Extract the embeddings from the model's output, which is the mean of the last hidden state
    embeddings = mean_pooling(outputs, inputs["attention_mask"])

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
