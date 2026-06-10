from pymongo.database import Database
from src.models.collection_models import InteractionEvent


class InteractionEventRepository:
    COLLECTION = "eventos_interaccion"

    def __init__(self, db: Database):
        self.collection = db[self.COLLECTION]

    def create(self, event: InteractionEvent) -> str:
        result = self.collection.insert_one(event.model_dump())
        return str(result.inserted_id)

    def find_by_id(self, event_id: str) -> dict | None:
        return self.collection.find_one({"event_id": event_id})

    def find_by_session(self, session_id: str) -> list[dict]:
        return list(self.collection.find({"session_id": session_id}))

    def find_by_student(self, student_id: str) -> list[dict]:
        return list(self.collection.find({"student_id": student_id}))

    def delete(self, event_id: str):
        self.collection.delete_one({"event_id": event_id})
