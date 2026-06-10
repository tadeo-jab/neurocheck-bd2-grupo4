from neo4j import Driver
from src.models.relationship_models import Explains


class ExplainsRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, resource_uid: str, concept_uid: str, rel: Explains):
        d = rel.model_dump()
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (r:Resource {uid: $ruid})
                    MATCH (c:Concept {uid: $cuid})
                    MERGE (r)-[e:EXPLAINS]->(c)
                    SET e.coverage = $coverage
                    """,
                    ruid=resource_uid, cuid=concept_uid, coverage=d["coverage"],
                )
            )

    def find_by_resource(self, resource_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (r:Resource {uid: $uid})-[e:EXPLAINS]->(c:Concept) RETURN c, e",
                uid=resource_uid,
            ).data()

    def delete(self, resource_uid: str, concept_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Resource {uid: $ruid})-[e:EXPLAINS]->(:Concept {uid: $cuid}) DELETE e",
                    ruid=resource_uid, cuid=concept_uid,
                )
            )
