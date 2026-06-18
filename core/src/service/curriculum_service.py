from src.db.neo4j import Neo4jService
from src.repository.neo4j.estudiante_repository import EstudianteRepository
from src.repository.neo4j.materia_repository import MateriaRepository
from src.repository.neo4j.materia_estudiante_repository import MateriaEstudianteRepository
from src.model.node_models import Materia


class CurriculumService:
    def __init__(self, neo4j: Neo4jService):
        self._estudiante_repo = EstudianteRepository(neo4j)
        self._materia_repo = MateriaRepository(neo4j)
        self._materia_estudiante_repo = MateriaEstudianteRepository(neo4j)

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


    def enroll_student(self, id_estudiante: str, id_materia: str) -> None:
        if not self._estudiante_repo.exists_by_id(id_estudiante):
            raise ValueError(f"Estudiante {id_estudiante} no encontrado")
        if not self._materia_repo.exists_by_id(id_materia):
            raise ValueError(f"Materia {id_materia} no encontrada")
        
        self._materia_estudiante_repo.set_student_enroll(id_estudiante, id_materia)