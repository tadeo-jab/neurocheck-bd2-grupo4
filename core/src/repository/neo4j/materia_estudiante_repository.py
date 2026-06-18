from core.src.db.neo4j import Neo4jService
from core.src.model.node_models import Materia


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
        return self._neo4j.read(query, id_estudiante=id_estudiante)



