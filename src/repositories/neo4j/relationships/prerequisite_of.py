from neo4j import Driver


class PrerequisiteOfRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, concept_uid: str, prerequisite_uid: str, required: bool = True):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    """
                    MATCH (c:Concept {uid: $cuid})
                    MATCH (p:Concept {uid: $puid})
                    MERGE (c)-[r:PREREQUISITE_OF]->(p)
                    SET r.required = $required
                    """,
                    cuid=concept_uid, puid=prerequisite_uid, required=required,
                )
            )

    def find_prerequisites(self, concept_uid: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (c:Concept {uid: $uid})-[r:PREREQUISITE_OF]->(p:Concept) RETURN p, r",
                uid=concept_uid,
            ).data()

    def delete(self, concept_uid: str, prerequisite_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (:Concept {uid: $cuid})-[r:PREREQUISITE_OF]->(:Concept {uid: $puid}) DELETE r",
                    cuid=concept_uid, puid=prerequisite_uid,
                )
            )
