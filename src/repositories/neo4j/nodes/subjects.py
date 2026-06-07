from neo4j import Driver


class SubjectNodeRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, uid: str, name: str, code: str) -> dict:
        with self.driver.session() as session:
            return session.execute_write(
                lambda tx: tx.run(
                    "CREATE (s:Subject {uid: $uid, name: $name, code: $code}) RETURN s",
                    uid=uid, name=name, code=code,
                ).single().data()
            )

    def find_by_uid(self, uid: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                "MATCH (s:Subject {uid: $uid}) RETURN s", uid=uid
            ).single()
            return result.data() if result else None

    def find_all(self) -> list[dict]:
        with self.driver.session() as session:
            return session.run("MATCH (s:Subject) RETURN s").data()

    def delete(self, uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (s:Subject {uid: $uid}) DETACH DELETE s", uid=uid
                )
            )
