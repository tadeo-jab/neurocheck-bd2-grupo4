from neo4j import Driver
from src.models.relationship_models import Evaluates


class EvaluatesRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, activity_uid: str, subject_uid: str, rel: Evaluates):
        d = rel.model_dump()
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (a:Activity {uid: $auid})
                    MATCH (s:Subject {uid: $suid})
                    MERGE (a)-[e:EVALUATES]->(s)
                    SET e.coverage = $coverage, e.approval_threshold = $at
                    """,
                    auid=activity_uid, suid=subject_uid, coverage=d["coverage"], at=d["approval_threshold"],
                )
            )

    def find_by_subject(self, subject_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (a:Activity)-[e:EVALUATES]->(s:Subject {uid: $uid}) RETURN a, e",
                uid=subject_uid,
            ).data()

    def delete(self, activity_uid: str, subject_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Activity {uid: $auid})-[e:EVALUATES]->(:Subject {uid: $suid}) DELETE e",
                    auid=activity_uid, suid=subject_uid,
                )
            )
