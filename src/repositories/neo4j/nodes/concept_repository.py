from neo4j import Driver
from src.models.node_models import Concept


class ConceptNodeRepo:
    def __init__(self, driver: Driver):
        self.driver = driver

    def create(self, concept: Concept) -> dict:
        d = concept.model_dump()
        with self.driver.session() as session:
            return session.execute_write(
                lambda tx: tx.run(
                    "CREATE (c:Concept {uid: $uid, name: $name, description: $desc, difficulty_level: $dl, estimated_time_minutes: $etm, usage_frequency: $uf}) RETURN c",
                    uid=d["uid"], name=d["name"], desc=d["description"], dl=d["difficulty_level"], etm=d["estimated_time_minutes"], uf=d["usage_frequency"],
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
