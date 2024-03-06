from pydantic_settings import BaseSettings


class NlpConfig(BaseSettings):
  """
  Configuration class for NLP module.
  """

  MODEL_NAME: str
  BUCKET_NAME: str
  CORPUS_DIR: str
  GCP_SA_KEY_BASE64: str 


  class Config:
    """
    Configuration class for Pydantic settings.
    """

    env_file = ".env"
    extra = "allow"


nlp_config = NlpConfig()
