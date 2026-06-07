from neo4j import Driver


class UsesRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, activity_uid: str, resource_uid: str, weight: float = 1.0):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (a:Activity {uid: $auid})
                    MATCH (r:Resource {uid: $ruid})
                    MERGE (a)-[u:USES]->(r)
                    SET u.weight = $weight
                    """,
                    auid=activity_uid, ruid=resource_uid, weight=weight,
                )
            )

    def find_by_activity(self, activity_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (a:Activity {uid: $uid})-[u:USES]->(r:Resource) RETURN r, u",
                uid=activity_uid,
            ).data()

    def delete(self, activity_uid: str, resource_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Activity {uid: $auid})-[u:USES]->(:Resource {uid: $ruid}) DELETE u",
                    auid=activity_uid, ruid=resource_uid,
                )
            )
