from neo4j import Driver
from src.models.node_models import Activity


class ActivityNodeRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, activity: Activity) -> dict:
        d = activity.model_dump()
        with self.driver.session() as session:
            return session.execute_write(
                lambda tx: tx.run(
                    "CREATE (a:Activity {uid: $uid, name: $name, description: $desc, type: $type, difficulty: $diff, estimated_time_minutes: $etm, cognitive_load: $cl, max_score: $ms}) RETURN a",
                    uid=d["uid"], name=d["name"], desc=d["description"], type=d["type"], diff=d["difficulty"], etm=d["estimated_time_minutes"], cl=d["cognitive_load"], ms=d["max_score"],
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
