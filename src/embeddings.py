from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def get_embedding(text):
  # Detailed explanation of the function's purpose
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
