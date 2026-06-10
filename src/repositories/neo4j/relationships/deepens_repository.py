from neo4j import Driver
from src.models.relationship_models import Deepens


class DeepensRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, advanced_uid: str, foundational_uid: str, rel: Deepens):
        d = rel.model_dump()
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (adv:Concept {uid: $adv_uid})
                    MATCH (found:Concept {uid: $found_uid})
                    MERGE (adv)-[r:DEEPENS]->(found)
                    SET r.complexity_factor = $cf
                    """,
                    adv_uid=advanced_uid, found_uid=foundational_uid, cf=d["complexity_factor"],
                )
            )

    def find_by_concept(self, concept_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (c:Concept {uid: $uid})-[r:DEEPENS]->(found:Concept) RETURN found, r",
                uid=concept_uid,
            ).data()

    def delete(self, advanced_uid: str, foundational_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Concept {uid: $adv_uid})-[r:DEEPENS]->(:Concept {uid: $found_uid}) DELETE r",
                    adv_uid=advanced_uid, found_uid=foundational_uid,
                )
            )
