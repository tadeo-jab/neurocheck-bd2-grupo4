from neo4j import Driver
from src.models.node_models import Resource


class ResourceNodeRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, resource: Resource) -> dict:
        d = resource.model_dump()
        with self.driver.session() as session:
            return session.execute_write(
                lambda tx: tx.run(
                    "CREATE (r:Resource {uid: $uid, type: $type, duration: $dur, cognitive_load: $cl, url: $url, optimal_learning_style: $ols}) RETURN r",
                    uid=d["uid"], type=d["type"], dur=d["duration"], cl=d["cognitive_load"], url=d["url"], ols=d["optimal_learning_style"],
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
