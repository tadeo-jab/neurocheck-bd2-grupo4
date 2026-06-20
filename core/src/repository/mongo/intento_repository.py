from datetime import datetime, timezone

from src.db.mongo import MongoService
from src.model.collection_models import Estudiante, Intento


class IntentoRepository:
    """Repository for the 'intentos' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def create_attempt(self, *, id: str, estudiante: Estudiante,
                       id_sesion: str, id_materia: str,
                       id_contenido: str, tipo_contenido: str,
                       inicio: datetime) -> None:
        doc = {
            "uid": id,
            "estudiante": estudiante.model_dump(),
            "id_sesion": id_sesion,
            "id_materia": id_materia,
            "id_contenido": id_contenido,
            "tipo_contenido": tipo_contenido,
            "inicio": inicio,
            "terminado": False,
            "duracion_segundos": 0,
            "pausas": 0,
            "duracion_pausa_segundos": 0,
        }
        self._mongo.db.intentos.insert_one(doc)

    def find_by_id(self, id_intento: str) -> dict | None:
        return self._mongo.db.intentos.find_one({"uid": id_intento})

    def get_last_attempts(self, student_id: str, limit: int) -> list[dict]:
        cursor = self._mongo.db.intentos.find(
            {"estudiante.uid": student_id},
            {"uid": 1, "aprobado": 1, "terminado": 1, "_id": 0},
        ).sort("inicio", -1).limit(limit)
        return list(cursor)

    def get_all_attempts(self, student_id: str) -> list[dict]:
        cursor = self._mongo.db.intentos.find(
            {"estudiante.uid": student_id},
            {"_id": 0},
        ).sort("inicio", -1)
        return list(cursor)

    def close_attempt(self, intento: Intento) -> None:
        datos = intento.model_dump(exclude={"uid", "estudiante", "id_sesion",
                                            "id_materia", "id_contenido",
                                            "tipo_contenido", "inicio"})
        self._mongo.db.intentos.update_one(
            {"uid": intento.uid},
            {"$set": datos}
        )
