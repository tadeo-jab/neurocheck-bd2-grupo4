from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str

    model_config = {"env_prefix": "NEUROCHECK_", "env_file": ".env"}


settings = Settings()
