from src.db.neo4j import Neo4jService
from src.model.node_models import Materia


class MateriaEstudianteRepository:
    """Repository for (:Materia), (:Estudiante) nodes and their relationships."""

    def __init__(self, neo4j: Neo4jService):
        self._neo4j = neo4j

    def get_student_nodes_status(self, id_estudiante: str) -> list[dict]:
        query = """
            MATCH (m:Materia)
            OPTIONAL MATCH (e:Estudiante {id: $id_estudiante})-[rel:ANOTADO_EN|COMPLETO]->(m)
            RETURN m.id AS id,
                   m.nombre AS nombre,
                   m.descripcion AS descripcion,
                   m.nivel_dificultad AS nivel_dificultad,
                   m.tiempo_estimado AS tiempo_estimado,
                   m.frecuencia_uso AS frecuencia_uso,
                   CASE
                     WHEN rel IS NULL THEN 'no_cursada'
                     WHEN rel.aprobado = true THEN 'aprobada'
                     WHEN rel.aprobado = false THEN 'reprobada'
                     WHEN rel.fecha_fin IS NULL THEN 'cursando'
                     ELSE 'completada'
                   END AS estado
        """
        params = {"id_estudiante": id_estudiante}
        print(f"[Neo4j] READ {query.strip()}\n       params={params}")
        return self._neo4j.read(query, **params)

    def get_student_currently_enrolled(self, id_estudiante: str) -> list[Materia]:
        query = """
            MATCH (e:Estudiante {id: $id_estudiante})-[rel:ANOTADO_EN]->(m:Materia)
            WHERE rel.completado = false
            RETURN m
        """
        params = {"id_estudiante": id_estudiante}
        print(f"[Neo4j] READ {query.strip()}\n       params={params}")
        resultados = self._neo4j.read(query, **params)
        return [Materia(**r["m"]) for r in resultados]

    def set_student_enroll(self, id_estudiante: str, id_materia: str, estilo_preferido: str) -> None:
        query = """
            MATCH (e:Estudiante {id: $id_estudiante}), (m:Materia {id: $id_materia})
            CREATE (e)-[:ANOTADO_EN {
                completado: false,
                fecha_inicio: datetime(),
                fecha_fin: null,
                estilo_actual: $estilo_preferido
            }]->(m)
        """
        params = {"id_estudiante": id_estudiante, "id_materia": id_materia, "estilo_preferido": estilo_preferido}
        print(f"[Neo4j] WRITE {query.strip()}\n       params={params}")
        self._neo4j.write(query, **params)

    def unenroll_student(self, id_estudiante: str, id_materia: str) -> None:
        query = """
            MATCH (e:Estudiante {id: $id_estudiante})-[rel:ANOTADO_EN]->(m:Materia {id: $id_materia})
            DELETE rel
        """
        params = {"id_estudiante": id_estudiante, "id_materia": id_materia}
        print(f"[Neo4j] WRITE {query.strip()}\n       params={params}")
        self._neo4j.write(query, **params)

    def get_enrollment_style(self, id_estudiante: str, id_materia: str) -> str | None:
        query = """
            MATCH (e:Estudiante {id: $id_estudiante})-[rel:ANOTADO_EN]->(m:Materia {id: $id_materia})
            RETURN rel.estilo_actual AS estilo
        """
        params = {"id_estudiante": id_estudiante, "id_materia": id_materia}
        print(f"[Neo4j] READ {query.strip()}\n       params={params}")
        resultados = self._neo4j.read(query, **params)
        return resultados[0]["estilo"] if resultados else None
