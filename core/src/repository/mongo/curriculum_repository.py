from src.db.mongo import MongoService
from src.model.collection_models import Actividad, CaminoAprendizaje, Recurso


class CurriculumRepository:
    """Repository for the 'curriculum' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def get_course_by_style(self, id_materia: str, estilo: str) -> CaminoAprendizaje | None:
        doc = self._mongo.db.curriculum.find_one(
            {"uid": id_materia},
            {f"caminos.{estilo}": 1}
        )
        if not doc:
            return None
        camino = doc.get("caminos", {}).get(estilo)
        return CaminoAprendizaje(**camino) if camino else None

    def get_resource(self, id_recurso: str) -> Recurso | None:
        doc = self._mongo.db.recursos.find_one({"uid": id_recurso})
        return Recurso(**doc) if doc else None

    def get_activity(self, id_actividad: str) -> Actividad | None:
        doc = self._mongo.db.actividades.find_one({"uid": id_actividad})
        return Actividad(**doc) if doc else None
    
    
