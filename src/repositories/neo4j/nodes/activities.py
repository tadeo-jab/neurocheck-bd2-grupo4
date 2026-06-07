from neo4j import Driver


class ActivityNodeRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, uid: str, name: str, type: str) -> dict:
        with self.driver.session() as session:
            return session.execute_write(
                lambda tx: tx.run(
                    "CREATE (a:Activity {uid: $uid, name: $name, type: $type}) RETURN a",
                    uid=uid, name=name, type=type,
                ).single().data()
            )

    def find_by_uid(self, uid: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                "MATCH (a:Activity {uid: $uid}) RETURN a", uid=uid
            ).single()
            return result.data() if result else None

    def find_by_type(self, type: str) -> list[dict]:
        with self.driver.session() as session:
            return session.run(
                "MATCH (a:Activity {type: $type}) RETURN a", type=type
            ).data()

    def delete(self, uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (a:Activity {uid: $uid}) DETACH DELETE a", uid=uid
                )
            )
