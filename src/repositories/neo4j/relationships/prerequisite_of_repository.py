from neo4j import Driver
from src.models.relationship_models import Requires


class RequiresRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, concept_uid: str, prerequisite_uid: str, rel: Requires):
        d = rel.model_dump()
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (c:Concept {uid: $cuid})
                    MATCH (p:Concept {uid: $puid})
                    MERGE (c)-[r:REQUIRES]->(p)
                    SET r.weight = $weight, r.level = $level, r.notes = $notes
                    """,
                    cuid=concept_uid, puid=prerequisite_uid,
                    weight=d["weight"], level=d["level"], notes=d["notes"],
                )
            )

    def find_prerequisites(self, concept_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (c:Concept {uid: $uid})-[r:REQUIRES]->(p:Concept) RETURN p, r",
                uid=concept_uid,
            ).data()

    def delete(self, concept_uid: str, prerequisite_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Concept {uid: $cuid})-[r:REQUIRES]->(:Concept {uid: $puid}) DELETE r",
                    cuid=concept_uid, puid=prerequisite_uid,
                )
            )
