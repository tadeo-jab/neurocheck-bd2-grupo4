from neo4j import Driver
from src.models.relationship_models import AlternativeTo


class AlternativeToRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, concept_uid: str, alternative_uid: str, rel: AlternativeTo):
        d = rel.model_dump()
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (c:Concept {uid: $cuid})
                    MATCH (alt:Concept {uid: $altuid})
                    MERGE (c)-[r:ALTERNATIVE_TO]->(alt)
                    SET r.additional_cost = $ac, r.favored_style = $fs
                    """,
                    cuid=concept_uid, altuid=alternative_uid, ac=d["additional_cost"], fs=d["favored_style"],
                )
            )

    def find_by_concept(self, concept_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (c:Concept {uid: $uid})-[r:ALTERNATIVE_TO]->(alt:Concept) RETURN alt, r",
                uid=concept_uid,
            ).data()

    def delete(self, concept_uid: str, alternative_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Concept {uid: $cuid})-[r:ALTERNATIVE_TO]->(:Concept {uid: $altuid}) DELETE r",
                    cuid=concept_uid, altuid=alternative_uid,
                )
            )
