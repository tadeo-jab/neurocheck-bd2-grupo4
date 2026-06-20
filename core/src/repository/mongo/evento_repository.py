from datetime import datetime, timezone

from src.db.mongo import MongoService
from src.model.collection_models import EventoInteraccion


class EventoRepository:
    """Repository for the 'eventos_interaccion' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def log_evento(self, evento: EventoInteraccion) -> None:
        doc = {
            "uid": evento.uid,
            "id_usuario": evento.id_usuario.uid,
            "nombre_usuario": evento.id_usuario.nombre,
            "id_sesion": evento.sesion.uid,
            "tipo_evento": evento.tipo_evento,
            "timestamp": evento.timestamp,
            "tema": getattr(evento, "tema", None),
            "id_contenido": getattr(evento, "id_contenido", None),
            "id_materia": getattr(evento, "id_materia", None),
        }
        self._mongo.db.eventos_interaccion.insert_one(doc)

    def log_raw(self, uid: str, id_usuario: str, nombre_usuario: str,
                id_sesion: str, tipo_evento: str,
                id_materia: str | None = None,
                id_contenido: str | None = None,
                tema: str | None = None) -> None:
        """Insert an event directly without a full model (used internally)."""
        self._mongo.db.eventos_interaccion.insert_one({
            "uid": uid,
            "id_usuario": id_usuario,
            "nombre_usuario": nombre_usuario,
            "id_sesion": id_sesion,
            "tipo_evento": tipo_evento,
            "timestamp": datetime.now(timezone.utc),
            "id_materia": id_materia,
            "id_contenido": id_contenido,
            "tema": tema,
        })

    def get_recent_events(self, student_id: str, limit: int = 20) -> list[dict]:
        """Consulta 4 — últimas interacciones de un estudiante, orden cronológico desc."""
        cursor = (
            self._mongo.db.eventos_interaccion
            .find({"id_usuario": student_id}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(limit)
        )
        return list(cursor)

    def get_events_for_difficulty(self, student_id: str,
                                  tema: str | None = None) -> list[dict]:
        """Consulta 3 — eventos para detectar dificultad (filtra por tema si se indica)."""
        filtro: dict = {"id_usuario": student_id}
        if tema:
            filtro["tema"] = tema
        cursor = (
            self._mongo.db.eventos_interaccion
            .find(filtro, {"_id": 0})
            .sort("timestamp", -1)
        )
        return list(cursor)
