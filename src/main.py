"""NeuroCheck — dual-database clinical/learning platform."""

from src.config import settings
from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService


def main():
    mongo = MongoService(settings.mongo_uri)
    neo4j = Neo4jService(
        settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password
    )

    with mongo, neo4j:
        print("NeuroCheck conectado — MongoDB + Neo4j listos.")


if __name__ == "__main__":
    main()
