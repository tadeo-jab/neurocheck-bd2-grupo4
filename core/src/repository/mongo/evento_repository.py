import uuid
from datetime import datetime, timezone

from src.db.mongo import MongoService
from src.model.collection_models import Estudiante, Sesion


class EventoRepository:
    """Repository for the 'eventos' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def create_event(self, *, tipo_evento: str, usuario: Estudiante,
                     sesion: Sesion) -> str:
        doc = {
            "uid": uuid.uuid4().hex,
            "id_usuario": usuario.model_dump(),
            "sesion": sesion.model_dump(),
            "tipo_evento": tipo_evento,
            "timestamp": datetime.now(timezone.utc),
        }
        self._mongo.db.eventos.insert_one(doc)
        print(f"[Mongo] db.eventos.insert_one({doc})")
        return doc["uid"]

    def get_events_by_student(self, estudiante_id: str,
                              limite: int = 50) -> list[dict]:
        cursor = self._mongo.db.eventos.find(
            {"id_usuario.uid": estudiante_id}
        ).sort("timestamp", -1).limit(limite)
        docs = list(cursor)
        for doc in docs:
            doc.pop("_id", None)
        print(f"[Mongo] db.eventos.find({{id_usuario.uid: {estudiante_id}}}) "
              f"→ {len(docs)} docs")
        return docs
