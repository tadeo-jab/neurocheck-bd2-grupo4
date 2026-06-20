from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService
from src.repository.mongo.estudiante_mdb_repository import EstudianteMDBRepository
from src.repository.mongo.evento_repository import EventoRepository
from src.repository.mongo.sesion_repository import SesionRepository
from src.repository.neo4j.estudiante_repository import EstudianteRepository
from src.repository.neo4j.materia_repository import MateriaRepository
from src.repository.neo4j.materia_estudiante_repository import MateriaEstudianteRepository
from src.model.node_models import Materia


class CurriculumService:
    def __init__(self, neo4j: Neo4jService, mongo: MongoService):
        self._estudiante_repo = EstudianteRepository(neo4j)
        self._materia_repo = MateriaRepository(neo4j)
        self._materia_estudiante_repo = MateriaEstudianteRepository(neo4j)
        self._estudiante_mdb_repo = EstudianteMDBRepository(mongo)
        self._sesion_repo = SesionRepository(mongo)
        self._evento_repo = EventoRepository(mongo)

    def get_student_enrollments(self, id_estudiante: str) -> list[Materia]:
        return self._materia_estudiante_repo.get_student_currently_enrolled(id_estudiante)

    def get_curriculum_tree(self, id_estudiante: str) -> dict:
        if not self._estudiante_repo.exists_by_id(id_estudiante):
            raise ValueError(f"Estudiante {id_estudiante} no encontrado")

        return {
            "nodos": self._materia_repo.get_all_subjects(),
            "aristas": self._materia_repo.get_all_subject_edges(),
            "estados": self._materia_estudiante_repo.get_student_nodes_status(id_estudiante),
        }

    def get_subject_tree(self, id_estudiante: str, id_materia: str) -> dict:
        if not self._estudiante_repo.exists_by_id(id_estudiante):
            raise ValueError(f"Estudiante {id_estudiante} no encontrado")
        if not self._materia_repo.exists_by_id(id_materia):
            raise ValueError(f"Materia {id_materia} no encontrada")

        nodos = self._materia_repo.get_related_subjects(id_materia)
        ids_relacionadas = {n.id for n in nodos}

        todos_estados = self._materia_estudiante_repo.get_student_nodes_status(id_estudiante)
        estados = [e for e in todos_estados if e["id"] in ids_relacionadas]

        return {
            "nodos": nodos,
            "aristas": self._materia_repo.get_related_edges(id_materia),
            "estados": estados,
        }

    def enroll_student(self, id_estudiante: str, id_materia: str,
                       estilo_preferido: str, sesion_id: str) -> None:
        if not self._estudiante_repo.exists_by_id(id_estudiante):
            raise ValueError(f"Estudiante {id_estudiante} no encontrado")
        if not self._materia_repo.exists_by_id(id_materia):
            raise ValueError(f"Materia {id_materia} no encontrada")

        self._materia_estudiante_repo.set_student_enroll(id_estudiante, id_materia, estilo_preferido)

        usuario = self._estudiante_mdb_repo.find_by_id(id_estudiante)
        sesion = self._sesion_repo.find_by_uid(sesion_id)
        if usuario and sesion:
            self._evento_repo.create_event(
                tipo_evento="enroll",
                usuario=usuario,
                sesion=sesion,
            )

    def switch_enrollment(self, id_estudiante: str, id_materia_old: str,
                          id_materia_new: str, estilo_aprendizaje: str,
                          sesion_id: str) -> None:
        self._materia_estudiante_repo.unenroll_student(id_estudiante, id_materia_old)
        self.enroll_student(id_estudiante, id_materia_new, estilo_aprendizaje, sesion_id)
