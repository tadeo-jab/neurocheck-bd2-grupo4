import bcrypt

from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.model.collection_models import Estudiante, Intento, Sesion
from src.repository.mongo.estudiante_mdb_repository import EstudianteMDBRepository
from src.repository.mongo.evento_repository import EventoRepository
from src.repository.mongo.sesion_repository import SesionRepository
from src.repository.neo4j.materia_repository import MateriaRepository


class AdminService:
    def __init__(self, mongo: MongoService, neo4j: Neo4jService):
        self._sesion_repo = SesionRepository(mongo)
        self._evento_repo = EventoRepository(mongo)
        self._estudiante_mdb_repo = EstudianteMDBRepository(mongo)
        self._materia_repo = MateriaRepository(neo4j)

    def get_sesiones_by_id(self, id_estudiante: str, limite: int = 10) -> list[Sesion]:
        return self._sesion_repo.get_student_sessions(id_estudiante, limite)

    def get_intentos_by_sesion(self, id_sesion: str) -> list[Intento]:
        return self._sesion_repo.get_current_attempts(id_sesion)

    def get_events(self, id_estudiante: str,
                   limite: int = 50) -> list[dict]:
        return self._evento_repo.get_events_by_student(id_estudiante, limite)

    def get_passed_count(self, id_estudiante: str) -> dict:
        estudiante = self._estudiante_mdb_repo.find_by_id(id_estudiante)
        aprobadas = self._materia_repo.get_passed_count(id_estudiante)
        return {"estudiante": estudiante, "aprobadas": aprobadas}

    def populate(self, estudiantes: list[dict], materias: list[dict],
                 prerrequisitos: list[dict]) -> None:
        # Inserción de estudiantes en MongoDB
        for e in estudiantes:
            self._estudiante_mdb_repo.insert(Estudiante(
                uid=e["id"],
                nombre=e["nombre"],
                email=e["email"],
                password_hash=bcrypt.hashpw(
                    e["password"].encode(), bcrypt.gensalt()
                ).decode(),
                estilo_preferido=e["estilo"],
            ))

        # Creación de temas en Neo4j
        for m in materias:
            self._materia_repo.create_subject(
                id=m["id"], nombre=m["nombre"],
                descripcion=m["desc"], nivel_dificultad=m["diff"],
                tiempo_estimado=m["horas"], frecuencia_uso=m["frec"],
            )

        # Creación de relaciones REQUIERE
        for origen, destino, peso, oblig, secuela in prerrequisitos:
            self._materia_repo.create_requires_relationship(
                origen=origen, destino=destino, peso=peso,
                obligatorio=oblig, secuela=secuela,
            )
