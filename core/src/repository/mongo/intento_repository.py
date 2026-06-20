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
            "pausa_inicio": None,
            "ultima_reanudacion": inicio,
        }
        self._mongo.db.intentos.insert_one(doc)
        print(f"[Mongo] db.intentos.insert_one({doc})")

    def find_by_id(self, id_intento: str) -> dict | None:
        filtro = {"uid": id_intento}
        doc = self._mongo.db.intentos.find_one(filtro)
        print(f"[Mongo] db.intentos.find_one({filtro})")
        return doc

    def pause_attempt(self, id_intento: str) -> dict | None:
        """Registra una pausa: acumula el tiempo activo transcurrido y marca pausa_inicio.
        Retorna el documento actualizado, o None si no existe."""
        ahora = datetime.now(timezone.utc)
        filtro = {"uid": id_intento}
        doc = self._mongo.db.intentos.find_one(filtro)
        print(f"[Mongo] db.intentos.find_one({filtro})")
        if not doc:
            return None
        ultima = doc["ultima_reanudacion"]
        if isinstance(ultima, str):
            ultima = datetime.fromisoformat(ultima)
        if ultima.tzinfo is None:
            ultima = ultima.replace(tzinfo=timezone.utc)
        elapsed = int((ahora - ultima).total_seconds())
        update = {"$inc": {"duracion_segundos": elapsed, "pausas": 1},
                  "$set": {"pausa_inicio": ahora}}
        self._mongo.db.intentos.update_one(filtro, update)
        print(f"[Mongo] db.intentos.update_one({filtro}, {update})")
        doc["duracion_segundos"] = doc.get("duracion_segundos", 0) + elapsed
        doc["pausas"] = doc.get("pausas", 0) + 1
        doc["pausa_inicio"] = ahora
        return doc

    def resume_attempt(self, id_intento: str) -> dict | None:
        """Reanuda tras una pausa: acumula la duración de la pausa y limpia pausa_inicio.
        Retorna el documento actualizado, o None si no existe o no estaba pausado."""
        ahora = datetime.now(timezone.utc)
        filtro = {"uid": id_intento}
        doc = self._mongo.db.intentos.find_one(filtro)
        print(f"[Mongo] db.intentos.find_one({filtro})")
        if not doc or not doc.get("pausa_inicio"):
            return None
        pausa_inicio = doc["pausa_inicio"]
        if isinstance(pausa_inicio, str):
            pausa_inicio = datetime.fromisoformat(pausa_inicio)
        if pausa_inicio.tzinfo is None:
            pausa_inicio = pausa_inicio.replace(tzinfo=timezone.utc)
        pausa_duracion = int((ahora - pausa_inicio).total_seconds())
        update = {"$inc": {"duracion_pausa_segundos": pausa_duracion},
                  "$set": {"pausa_inicio": None, "ultima_reanudacion": ahora}}
        self._mongo.db.intentos.update_one(filtro, update)
        print(f"[Mongo] db.intentos.update_one({filtro}, {update})")
        doc["duracion_pausa_segundos"] = doc.get("duracion_pausa_segundos", 0) + pausa_duracion
        doc["pausa_inicio"] = None
        doc["ultima_reanudacion"] = ahora
        return doc

    def get_last_attempts(self, student_id: str, limit: int) -> list[dict]:
        filtro = {"estudiante.uid": student_id}
        proyeccion = {"uid": 1, "aprobado": 1, "terminado": 1, "_id": 0}
        cursor = self._mongo.db.intentos.find(filtro, proyeccion).sort("inicio", -1).limit(limit)
        print(f"[Mongo] db.intentos.find({filtro}, {proyeccion}).sort('inicio', -1).limit({limit})")
        return list(cursor)

    def close_attempt(self, intento: Intento) -> None:
        datos = intento.model_dump(exclude={"uid", "estudiante", "id_sesion",
                                            "id_materia", "id_contenido",
                                            "tipo_contenido", "inicio"})
        filtro = {"uid": intento.uid}
        update = {"$set": datos}
        self._mongo.db.intentos.update_one(filtro, update)
        print(f"[Mongo] db.intentos.update_one({filtro}, {update})")
