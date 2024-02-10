from scipy.spatial.distance import cosine

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
