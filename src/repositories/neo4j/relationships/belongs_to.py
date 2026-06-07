from neo4j import Driver


class BelongsToRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, node_uid: str, node_label: str, subject_uid: str, primary: bool = False):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    f"""
                    MATCH (n:{node_label} {{uid: $nuid}})
                    MATCH (s:Subject {{uid: $suid}})
                    MERGE (n)-[b:BELONGS_TO]->(s)
                    SET b.primary = $primary
                    """,
                    nuid=node_uid, suid=subject_uid, primary=primary,
                )
            )

    def find_by_subject(self, subject_uid: str, node_label: str = "Concept") -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                f"MATCH (n:{node_label})-[b:BELONGS_TO]->(s:Subject {{uid: $uid}}) RETURN n, b",
                uid=subject_uid,
            ).data()

    def delete(self, node_uid: str, node_label: str, subject_uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    f"MATCH (n:{node_label} {{uid: $nuid}})-[b:BELONGS_TO]->(:Subject {{uid: $suid}}) DELETE b",
                    nuid=node_uid, suid=subject_uid,
                )
            )
