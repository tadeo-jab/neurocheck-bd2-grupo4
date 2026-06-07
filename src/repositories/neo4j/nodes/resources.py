from neo4j import Driver


class ResourceNodeRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, uid: str, title: str, url: str) -> dict:
        with self.driver.session() as session:
            return session.execute_write(
                lambda tx: tx.run(
                    "CREATE (r:Resource {uid: $uid, title: $title, url: $url}) RETURN r",
                    uid=uid, title=title, url=url,
                ).single().data()
            )

    def find_by_uid(self, uid: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                "MATCH (r:Resource {uid: $uid}) RETURN r", uid=uid
            ).single()
            return result.data() if result else None

    def delete(self, uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (r:Resource {uid: $uid}) DETACH DELETE r", uid=uid
                )
            )
