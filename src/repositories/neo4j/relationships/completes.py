from neo4j import Driver


class CompletesRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, student_uid: str, activity_uid: str, score: float = 0.0):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (s:Student {uid: $suid})
                    MATCH (a:Activity {uid: $auid})
                    MERGE (s)-[r:COMPLETES]->(a)
                    SET r.score = $score, r.completed_at = datetime()
                    """,
                    suid=student_uid, auid=activity_uid, score=score,
                )
            )

    def find_by_student(self, student_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (s:Student {uid: $uid})-[r:COMPLETES]->(a:Activity) RETURN a, r",
                uid=student_uid,
            ).data()

    def delete(self, student_uid: str, activity_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Student {uid: $suid})-[r:COMPLETES]->(:Activity {uid: $auid}) DELETE r",
                    suid=student_uid, auid=activity_uid,
                )
            )
