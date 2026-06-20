from datetime import datetime, timezone

from src.db.mongo import MongoService
from src.model.collection_models import Intento, Sesion


class SesionRepository:
    """Repository for the 'sesiones' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def create_session(self, sesion: Sesion) -> None:
        self._mongo.db.sesiones.insert_one(sesion.model_dump())

    def add_attempt_session(self, id_sesion: str, intento: Intento) -> None:
        self._mongo.db.sesiones.update_one(
            {"uid": id_sesion},
            {"$push": {"intentos_estudio": intento.model_dump()}}
        )

    def end_session(self, id_sesion: str) -> None:
        self._mongo.db.sesiones.update_one(
            {"uid": id_sesion},
            {"$set": {"fecha_fin": datetime.now(timezone.utc)}}
        )

    def get_current_attempts(self, id_sesion: str) -> list[Intento]:
        doc = self._mongo.db.sesiones.find_one({"uid": id_sesion})
        if not doc or "intentos_estudio" not in doc:
            return []
        return [Intento(**i) for i in doc["intentos_estudio"]]

    def get_student_sessions(self, id_estudiante: str, limite: int) -> list[Sesion]:
        cursor = (
            self._mongo.db.sesiones.find({"estudiante.uid": id_estudiante})
            .sort("fecha_ini", -1)
            .limit(limite)
        )
        return [Sesion(**doc) for doc in cursor]
