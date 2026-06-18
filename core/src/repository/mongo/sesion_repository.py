from datetime import datetime, timezone

from src.db.mongo import MongoService
from src.model.collection_models import Intento, Sesion


class SesionRepository:
    """Repository for the 'sesiones' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def create_session(self, sesion: Sesion) -> None:
        doc = sesion.model_dump()
        doc["_id"] = sesion.id
        self._mongo.db.sesiones.insert_one(doc)

    def add_attempt_session(self, id_sesion: str, intento: Intento) -> None:
        self._mongo.db.sesiones.update_one(
            {"_id": id_sesion},
            {"$push": {"intentos_estudio": intento.model_dump()}}
        )

    def end_session(self, id_sesion: str) -> None:
        self._mongo.db.sesiones.update_one(
            {"_id": id_sesion},
            {"$set": {"fecha_fin": datetime.now(timezone.utc)}}
        )
