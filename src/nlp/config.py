from pydantic_settings import BaseSettings


class NlpConfig(BaseSettings):
  """
  Configuration class for NLP module.
  """

  MODEL_NAME: str
  MODEL_DIR: str
  CORPUS_DIR: str

  class Config:
    """
    Configuration class for Pydantic settings.
    """

    env_file = ".env"
    extra = "allow"


nlp_config = NlpConfig()
