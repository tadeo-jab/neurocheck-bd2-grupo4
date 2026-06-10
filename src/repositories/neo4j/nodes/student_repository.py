from neo4j import Driver
from src.models.node_models import Student


class StudentNodeRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, student: Student) -> dict:
        d = student.model_dump()
        with self.driver.session() as session:
            return session.execute_write(
                lambda tx: tx.run(
                    "CREATE (s:Student {uid: $uid, name: $name, mastery_level: $ml, preferred_style: $ps, current_session_id: $csid}) RETURN s",
                    uid=d["uid"], name=d["name"], ml=d["mastery_level"], ps=d["preferred_style"], csid=d["current_session_id"],
                ).single().data()
            )

    def find_by_uid(self, uid: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                "MATCH (s:Student {uid: $uid}) RETURN s", uid=uid
            ).single()
            return result.data() if result else None

    def find_all(self) -> list[dict]:
        with self.driver.session() as session:
            return session.run("MATCH (s:Student) RETURN s").data()

    def delete(self, uid: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (s:Student {uid: $uid}) DETACH DELETE s", uid=uid
                )
            )
