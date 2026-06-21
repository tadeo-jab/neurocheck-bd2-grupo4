import json

from src.db.mongo import MongoService
from src.model.collection_models import Actividad, CaminoAprendizaje, Recurso


class CurriculumRepository:
    """Repository for the 'curriculum' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def get_course_by_style(self, id_materia: str, estilo: str) -> CaminoAprendizaje | None:
        filtro = {"uid": id_materia}
        proyeccion = {f"caminos.{estilo}": 1}
        doc = self._mongo.db.curriculum.find_one(filtro, proyeccion)
        print(f"[Mongo] db.curriculum.find_one({json.dumps(filtro, ensure_ascii=False)}, "
              f"{json.dumps(proyeccion, ensure_ascii=False)})")
        if not doc:
            return None
        camino = doc.get("caminos", {}).get(estilo)
        return CaminoAprendizaje(**camino) if camino else None

    def get_resource(self, id_recurso: str) -> Recurso | None:
        filtro = {"uid": id_recurso}
        doc = self._mongo.db.recursos.find_one(filtro)
        print(f"[Mongo] db.recursos.find_one({json.dumps(filtro, ensure_ascii=False)})")
        return Recurso(**doc) if doc else None

    def get_activity(self, id_actividad: str) -> Actividad | None:
        filtro = {"uid": id_actividad}
        doc = self._mongo.db.actividades.find_one(filtro)
        print(f"[Mongo] db.actividades.find_one({json.dumps(filtro, ensure_ascii=False)})")
        return Actividad(**doc) if doc else None
