from src.db.mongo import MongoService
from src.model.collection_models import Estudiante


class EstudianteMDBRepository:
    """Repository for the 'estudiantes' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def find_by_email(self, email: str) -> Estudiante | None:
        doc = self._mongo.db.estudiantes.find_one({"email": email})
        return Estudiante(**doc) if doc else None

    def find_by_id(self, id: str) -> Estudiante | None:
        doc = self._mongo.db.estudiantes.find_one({"_id": id})
        return Estudiante(**doc) if doc else None

    def insert(self, estudiante: Estudiante) -> None:
        self._mongo.db.estudiantes.insert_one(estudiante.model_dump(by_alias=True))
