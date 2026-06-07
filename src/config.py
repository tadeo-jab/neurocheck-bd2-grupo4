from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str = "mongodb://neurocheckMongo:neurocheck@localhost:27017"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neurocheck"

    model_config = {"env_prefix": "NEUROCHECK_", "env_file": ".env"}


settings = Settings()
