from datetime import datetime, timezone

from src.db.mongo import MongoService
from src.model.collection_models import Intento, Sesion


class SesionRepository:
    """Repository for the 'sesiones' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def create_session(self, sesion: Sesion) -> None:
        doc = sesion.model_dump()
        self._mongo.db.sesiones.insert_one(doc)
        print(f"[Mongo] db.sesiones.insert_one({doc})")

    def add_attempt_session(self, id_sesion: str, intento: Intento) -> None:
        filtro = {"uid": id_sesion}
        update = {"$push": {"intentos_estudio": intento.model_dump()}}
        self._mongo.db.sesiones.update_one(filtro, update)
        print(f"[Mongo] db.sesiones.update_one({filtro}, {update})")

    def end_session(self, id_sesion: str) -> None:
        filtro = {"uid": id_sesion}
        update = {"$set": {"fecha_fin": datetime.now(timezone.utc)}}
        self._mongo.db.sesiones.update_one(filtro, update)
        print(f"[Mongo] db.sesiones.update_one({filtro}, {update})")

    def get_current_attempts(self, id_sesion: str) -> list[Intento]:
        filtro = {"uid": id_sesion}
        doc = self._mongo.db.sesiones.find_one(filtro)
        print(f"[Mongo] db.sesiones.find_one({filtro})")
        if not doc or "intentos_estudio" not in doc:
            return []
        return [Intento(**i) for i in doc["intentos_estudio"]]

    def find_by_token(self, token: str) -> dict | None:
        filtro = {"token": token}
        doc = self._mongo.db.sesiones.find_one(filtro)
        print(f"[Mongo] db.sesiones.find_one({filtro})")
        return doc

    def get_student_sessions(self, id_estudiante: str, limite: int) -> list[Sesion]:
        filtro = {"estudiante.uid": id_estudiante}
        cursor = (
            self._mongo.db.sesiones.find(filtro)
            .sort("fecha_ini", -1)
            .limit(limite)
        )
        print(f"[Mongo] db.sesiones.find({filtro}).sort('fecha_ini', -1).limit({limite})")
        return [Sesion(**doc) for doc in cursor]
