from pymongo.database import Database


class StudentConfigRepository:
    COLLECTION = "student_config"

    def __init__(self, db: Database):
        self.collection = db[self.COLLECTION]

    def find_by_student(self, student_id: str) -> dict | None:
        return self.collection.find_one({"student_id": student_id})

    def upsert(self, student_id: str, config: dict):
        self.collection.update_one(
            {"student_id": student_id}, {"$set": config}, upsert=True
        )

    def delete(self, student_id: str):
        self.collection.delete_one({"student_id": student_id})
