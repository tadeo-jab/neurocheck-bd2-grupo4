from neo4j import Driver
from src.models.relationship_models import CorrelatesWith


class CorrelatesWithRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, concept_a_uid: str, concept_b_uid: str, rel: CorrelatesWith):
        d = rel.model_dump()
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (a:Concept {uid: $auid})
                    MATCH (b:Concept {uid: $buid})
                    MERGE (a)-[r:CORRELATES_WITH]->(b)
                    SET r.strength = $strength
                    """,
                    auid=concept_a_uid, buid=concept_b_uid, strength=d["strength"],
                )
            )

    def find_by_concept(self, concept_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (c:Concept {uid: $uid})-[r:CORRELATES_WITH]->(other:Concept) RETURN other, r",
                uid=concept_uid,
            ).data()

    def delete(self, concept_a_uid: str, concept_b_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Concept {uid: $auid})-[r:CORRELATES_WITH]->(:Concept {uid: $buid}) DELETE r",
                    auid=concept_a_uid, buid=concept_b_uid,
                )
            )
