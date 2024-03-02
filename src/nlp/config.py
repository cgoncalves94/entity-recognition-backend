from pydantic_settings import BaseSettings

class NlpConfig(BaseSettings):
    MODEL_NAME: str
    MODEL_DIR: str
    CORPUS_DIR: str

    class Config:
        env_file = ".env"
        extra = "allow"  

nlp_config = NlpConfig()
