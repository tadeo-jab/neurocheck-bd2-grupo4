from neo4j import Driver


class LearnsRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, student_uid: str, concept_uid: str, confidence: float = 0.0):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (s:Student {uid: $suid})
                    MATCH (c:Concept {uid: $cuid})
                    MERGE (s)-[r:LEARNS]->(c)
                    SET r.confidence = $confidence, r.since = datetime()
                    """,
                    suid=student_uid, cuid=concept_uid, confidence=confidence,
                )
            )

    def find_by_student(self, student_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (s:Student {uid: $uid})-[r:LEARNS]->(c:Concept) RETURN c, r",
                uid=student_uid,
            ).data()

    def delete(self, student_uid: str, concept_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Student {uid: $suid})-[r:LEARNS]->(:Concept {uid: $cuid}) DELETE r",
                    suid=student_uid, cuid=concept_uid,
                )
            )
