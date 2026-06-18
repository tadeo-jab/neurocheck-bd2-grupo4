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
            "_id": id,
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
        return self._mongo.db.intentos.find_one({"_id": id_intento})

    def close_attempt(self, intento: Intento) -> None:
        datos = intento.model_dump(exclude={"id", "estudiante", "id_sesion",
                                            "id_materia", "id_contenido",
                                            "tipo_contenido", "inicio"})
        self._mongo.db.intentos.update_one(
            {"_id": intento.id},
            {"$set": datos}
        )
