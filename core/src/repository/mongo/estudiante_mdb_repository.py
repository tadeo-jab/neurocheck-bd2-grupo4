from src.db.mongo import MongoService
from src.model.collection_models import Estudiante


class EstudianteMDBRepository:
    """Repository for the 'estudiantes' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def find_by_email(self, email: str) -> Estudiante | None:
        filtro = {"email": email}
        doc = self._mongo.db.estudiantes.find_one(filtro)
        print(f"[Mongo] db.estudiantes.find_one({filtro})")
        return Estudiante(**doc) if doc else None

    def find_by_id(self, id: str) -> Estudiante | None:
        filtro = {"uid": id}
        doc = self._mongo.db.estudiantes.find_one(filtro)
        print(f"[Mongo] db.estudiantes.find_one({filtro})")
        return Estudiante(**doc) if doc else None

    def insert(self, estudiante: Estudiante) -> None:
        doc = estudiante.model_dump()
        self._mongo.db.estudiantes.insert_one(doc)
        print(f"[Mongo] db.estudiantes.insert_one({doc})")
