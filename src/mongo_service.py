from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


class MongoService:
    """MongoDB service for NeuroCheck — perfiles, sesiones y eventos de interacción."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        username: str = "neurocheckMongo",
        password: str = "neurocheck",
        database: str = "neurocheck",
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._database_name = database
        self._client: MongoClient | None = None
        self._db: Database | None = None

    # -- connection lifecycle -------------------------------------------------

    @property
    def client(self) -> MongoClient:
        if self._client is None:
            raise RuntimeError("MongoService is not connected. Call connect() first.")
        return self._client

    @property
    def db(self) -> Database:
        if self._db is None:
            raise RuntimeError("MongoService is not connected. Call connect() first.")
        return self._db

    def connect(self) -> MongoService:
        self._client = MongoClient(
            host=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            authSource="admin",
        )
        self._db = self._client[self._database_name]
        self._client.admin.command("ping")
        return self

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None

    @contextmanager
    def session(self) -> Iterator[MongoService]:
        self.connect()
        try:
            yield self
        finally:
            self.disconnect()

    def collection(self, name: str) -> Collection:
        return self.db[name]

    # -- indexes --------------------------------------------------------------

    def create_indexes(self) -> None:
        """Create the indexes defined in the conceptual design (Etapa 1)."""
        self.collection("sesiones_estudio").create_index(
            [("id_usuario", ASCENDING), ("fecha", DESCENDING)]
        )
        self.collection("eventos_interaccion").create_index(
            [("id_usuario", ASCENDING), ("timestamp", DESCENDING)]
        )
        self.collection("eventos_interaccion").create_index(
            [("tema", ASCENDING), ("tipo_evento", ASCENDING)]
        )

    # -- generic CRUD ---------------------------------------------------------

    def insert_one(self, collection: str, document: dict[str, Any]) -> str:
        result = self.collection(collection).insert_one(document)
        return str(result.inserted_id)

    def insert_many(self, collection: str, documents: list[dict[str, Any]]) -> list[str]:
        result = self.collection(collection).insert_many(documents)
        return [str(oid) for oid in result.inserted_ids]

    def find_one(self, collection: str, query: dict[str, Any]) -> dict[str, Any] | None:
        return self.collection(collection).find_one(query)

    def find(
        self,
        collection: str,
        query: dict[str, Any],
        *,
        limit: int = 0,
        skip: int = 0,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[dict[str, Any]]:
        cursor = self.collection(collection).find(query)
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def update_one(
        self, collection: str, query: dict[str, Any], update: dict[str, Any]
    ) -> int:
        result = self.collection(collection).update_one(query, update)
        return result.modified_count

    def delete_one(self, collection: str, query: dict[str, Any]) -> int:
        result = self.collection(collection).delete_one(query)
        return result.deleted_count

    # -- consultas especificas del dominio ------------------------------------

    # Consulta 1 — Recuperar perfil completo del estudiante
    def get_student_profile(self, id_usuario: int) -> dict[str, Any] | None:
        return self.collection("estudiantes").find_one({"_id": id_usuario})

    # Consulta 2 — Obtener historial de sesiones de estudio
    def get_study_history(
        self,
        id_usuario: int,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"id_usuario": id_usuario}
        if fecha_desde or fecha_hasta:
            query["fecha"] = {}
            if fecha_desde:
                query["fecha"]["$gte"] = fecha_desde
            if fecha_hasta:
                query["fecha"]["$lte"] = fecha_hasta
        return list(
            self.collection("sesiones_estudio")
            .find(query)
            .sort("fecha", DESCENDING)
        )

    # Consulta 3 — Detectar posibles dificultades de aprendizaje
    def detect_difficulties(
        self,
        id_usuario: int | None = None,
        tema: str | None = None,
        fecha_desde: str | None = None,
    ) -> list[dict[str, Any]]:
        match: dict[str, Any] = {}
        if id_usuario is not None:
            match["id_usuario"] = id_usuario
        if tema is not None:
            match["tema"] = tema
        if fecha_desde is not None:
            match["timestamp"] = {"$gte": fecha_desde}

        pipeline: list[dict[str, Any]] = [{"$match": match}]

        # aggregate low-performance signals
        pipeline.append({
            "$addFields": {
                "_bajo_rendimiento": {
                    "$or": [
                        {"$and": [
                            {"$gte": ["$intentos", 3]},
                            {"$lt": ["$porcentaje_aciertos", 50]},
                        ]},
                        {"$eq": ["$estado", "abandonado"]},
                        {"$gte": ["$errores", 5]},
                    ]
                }
            }
        })
        pipeline.append({"$match": {"_bajo_rendimiento": True}})

        return list(self.collection("eventos_interaccion").aggregate(pipeline))

    # Consulta 4 — Obtener eventos recientes de un estudiante
    def get_recent_events(
        self, id_usuario: int, limit: int = 20
    ) -> list[dict[str, Any]]:
        return list(
            self.collection("eventos_interaccion")
            .find({"id_usuario": id_usuario})
            .sort("timestamp", DESCENDING)
            .limit(limit)
        )

    # -- consultas analiticas -------------------------------------------------

    def topics_by_difficulty(self) -> list[dict[str, Any]]:
        """Temas que generan mayor dificultad (errores > aciertos agrupados)."""
        pipeline: list[dict[str, Any]] = [
            {"$match": {"tipo_evento": "quiz_resuelto"}},
            {"$group": {
                "_id": "$tema",
                "promedio_aciertos": {"$avg": "$porcentaje_aciertos"},
                "total_intentos": {"$sum": "$intentos"},
                "total_abandonos": {
                    "$sum": {"$cond": [{"$eq": ["$estado", "abandonado"]}, 1, 0]}
                },
                "cantidad": {"$sum": 1},
            }},
            {"$sort": {"promedio_aciertos": 1}},
        ]
        return list(self.collection("eventos_interaccion").aggregate(pipeline))

    def weekly_performance(self, id_usuario: int) -> list[dict[str, Any]]:
        """Evolucion semanal del rendimiento de un estudiante."""
        pipeline: list[dict[str, Any]] = [
            {"$match": {"id_usuario": id_usuario, "porcentaje_aciertos": {"$exists": True}}},
            {"$group": {
                "_id": {"$substr": ["$timestamp", 0, 7]},  # YYYY-MM
                "promedio_aciertos": {"$avg": "$porcentaje_aciertos"},
                "total_eventos": {"$sum": 1},
            }},
            {"$sort": {"_id": 1}},
        ]
        return list(self.collection("eventos_interaccion").aggregate(pipeline))
