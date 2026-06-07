from pymongo.database import Database


class SessionRepository:
    COLLECTION = "Sessions"

    def __init__(self, db: Database):
        self.collection = db[self.COLLECTION]

    def create(self, document: dict) -> str:
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def find_by_id(self, session_id: str) -> dict | None:
        return self.collection.find_one({"session_id": session_id})

    def find_by_student(self, student_id: str) -> list[dict]:
        return list(self.collection.find({"student_id": student_id}))

    def update(self, session_id: str, update: dict):
        self.collection.update_one({"session_id": session_id}, {"$set": update})

    def delete(self, session_id: str):
        self.collection.delete_one({"session_id": session_id})
