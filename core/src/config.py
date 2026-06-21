from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Bases de datos
    mongo_uri: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str

    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_prefix": "NEUROCHECK_", "env_file": ".env"}


settings = Settings()
