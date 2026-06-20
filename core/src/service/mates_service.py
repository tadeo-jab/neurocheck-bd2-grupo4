from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.repository.mongo.estudiante_mdb_repository import EstudianteMDBRepository
from src.repository.mongo.evento_repository import EventoRepository
from src.repository.mongo.sesion_repository import SesionRepository
from src.repository.neo4j.estudiante_repository import EstudianteRepository


class MatesService:
    _LIMITE_SUGERENCIAS = 15

    def __init__(self, neo4j: Neo4jService, mongo: MongoService):
        self._estudiante_repo = EstudianteRepository(neo4j)
        self._estudiante_mdb_repo = EstudianteMDBRepository(mongo)
        self._sesion_repo = SesionRepository(mongo)
        self._evento_repo = EventoRepository(mongo)

    def get_student_mates(self, id_estudiante: str) -> list[dict]:
        return self._estudiante_repo.get_mate_by_id(id_estudiante)

    def suggested_mates(self, id_estudiante: str) -> list[dict]:
        return self._estudiante_repo.recommend_mates(id_estudiante, limite=self._LIMITE_SUGERENCIAS)

    def send_mate_request(self, student_id_a: str, student_id_b: str,
                          sesion_id: str) -> None:
        if not self._estudiante_repo.exists_by_id(student_id_a):
            raise ValueError(f"Estudiante {student_id_a} no encontrado")

        if not self._estudiante_repo.exists_by_id(student_id_b):
            raise ValueError(f"Estudiante {student_id_b} no encontrado")

        self._estudiante_repo.request_mate(student_id_a, student_id_b)

        usuario = self._estudiante_mdb_repo.find_by_id(student_id_a)
        sesion = self._sesion_repo.find_by_uid(sesion_id)
        if usuario and sesion:
            self._evento_repo.create_event(
                tipo_evento="mate_request",
                usuario=usuario,
                sesion=sesion,
            )


    