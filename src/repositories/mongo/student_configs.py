from pymongo.database import Database
from src.models.collection_models import Student


class StudentRepository:
    COLLECTION = "estudiantes"

    def __init__(self, db: Database):
        self.collection = db[self.COLLECTION]

    def create(self, student: Student) -> str:
        result = self.collection.insert_one(student.model_dump())
        return str(result.inserted_id)

    def find_by_id(self, student_id: str) -> dict | None:
        return self.collection.find_one({"id": student_id})

    def find_all(self) -> list[dict]:
        return list(self.collection.find())

    def update(self, student_id: str, update: dict):
        self.collection.update_one({"id": student_id}, {"$set": update})

    def delete(self, student_id: str):
        self.collection.delete_one({"id": student_id})
