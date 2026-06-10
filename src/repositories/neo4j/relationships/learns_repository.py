from neo4j import Driver
from src.models.relationship_models import Studies


class StudiesRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, student_uid: str, concept_uid: str, rel: Studies):
        d = rel.model_dump()
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (s:Student {uid: $suid})
                    MATCH (c:Concept {uid: $cuid})
                    MERGE (s)-[r:STUDIES]->(c)
                    SET r.total_time_minutes = $ttm, r.last_studied_at = datetime(),
                        r.times_studied = $ts, r.mastery_level = $ml
                    """,
                    suid=student_uid, cuid=concept_uid,
                    ttm=d["total_time_minutes"], ts=d["times_studied"], ml=d["mastery_level"],
                )
            )

    def find_by_student(self, student_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (s:Student {uid: $uid})-[r:STUDIES]->(c:Concept) RETURN c, r",
                uid=student_uid,
            ).data()

    def delete(self, student_uid: str, concept_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Student {uid: $suid})-[r:STUDIES]->(:Concept {uid: $cuid}) DELETE r",
                    suid=student_uid, cuid=concept_uid,
                )
            )
