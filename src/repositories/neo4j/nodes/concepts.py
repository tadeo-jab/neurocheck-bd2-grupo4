from neo4j import Driver


class ConceptNodeRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, uid: str, name: str, description: str = "") -> dict:
        with self.driver.session() as session:
            return session.execute_write(
                lambda tx: tx.run(
                    "CREATE (c:Concept {uid: $uid, name: $name, description: $desc}) RETURN c",
                    uid=uid, name=name, desc=description,
                ).single().data()
            )

    def find_by_uid(self, uid: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                "MATCH (c:Concept {uid: $uid}) RETURN c", uid=uid
            ).single()
            return result.data() if result else None

    def find_all(self) -> list[dict]:
        with self.driver.session() as session:
            return session.run("MATCH (c:Concept) RETURN c").data()

    def delete(self, uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (c:Concept {uid: $uid}) DETACH DELETE c", uid=uid
                )
            )
