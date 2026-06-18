from core.src.db.mongo import MongoService
from core.src.model.collection_models import CaminoAprendizaje


class CurriculumRepository:
    """Repository for the 'curriculum' MongoDB collection."""

    def __init__(self, mongo: MongoService):
        self._mongo = mongo

    def get_camino_por_estilo(self, id_materia: str, estilo: str) -> CaminoAprendizaje | None:
        doc = self._mongo.db.curriculum.find_one(
            {"_id": id_materia},
            {f"caminos.{estilo}": 1}
        )
        if not doc:
            return None
        camino = doc.get("caminos", {}).get(estilo)
        return CaminoAprendizaje(**camino) if camino else None
