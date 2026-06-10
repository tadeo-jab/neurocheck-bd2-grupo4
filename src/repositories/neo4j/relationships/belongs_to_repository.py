from neo4j import Driver
from src.models.relationship_models import BelongsTo


class BelongsToRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, concept_uid: str, subject_uid: str, rel: BelongsTo):
        d = rel.model_dump()
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (c:Concept {uid: $cuid})
                    MATCH (s:Subject {uid: $suid})
                    MERGE (c)-[b:BELONGS_TO]->(s)
                    SET b.weight_in_subject = $wis
                    """,
                    cuid=concept_uid, suid=subject_uid, wis=d["weight_in_subject"],
                )
            )

    def find_by_subject(self, subject_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (c:Concept)-[b:BELONGS_TO]->(s:Subject {uid: $uid}) RETURN c, b",
                uid=subject_uid,
            ).data()

    def delete(self, concept_uid: str, subject_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Concept {uid: $cuid})-[b:BELONGS_TO]->(:Subject {uid: $suid}) DELETE b",
                    cuid=concept_uid, suid=subject_uid,
                )
            )
