from pydantic_settings import BaseSettings


class NlpConfig(BaseSettings):
    """
    Configuration class for NLP module.
    """

    MODEL_NAME: str
    CORPUS_DIR: str
    BLUEPRINTS_DIR: str


nlp_config = NlpConfig()
