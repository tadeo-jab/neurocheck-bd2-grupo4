from src.db.mongo import MongoService
from src.model.collection_models import Intento, Sesion
from src.repository.mongo.evento_repository import EventoRepository
from src.repository.mongo.sesion_repository import SesionRepository


class AdminService:
    def __init__(self, mongo: MongoService):
        self._sesion_repo = SesionRepository(mongo)
        self._evento_repo = EventoRepository(mongo)

    def get_sesiones_by_id(self, id_estudiante: str, limite: int = 10) -> list[Sesion]:
        return self._sesion_repo.get_student_sessions(id_estudiante, limite)

    def get_intentos_by_sesion(self, id_sesion: str) -> list[Intento]:
        return self._sesion_repo.get_current_attempts(id_sesion)

    def get_events(self, id_estudiante: str,
                   limite: int = 50) -> list[dict]:
        return self._evento_repo.get_events_by_student(id_estudiante, limite)
