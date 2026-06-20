from src.db.neo4j import Neo4jService
from src.model.node_models import Materia


class MateriaEstudianteRepository:
    """Repository for (:Materia), (:Estudiante) nodes and their relationships."""

    def __init__(self, neo4j: Neo4jService):
        self._neo4j = neo4j

    def get_student_nodes_status(self, id_estudiante: str) -> list[dict]:
        query = """
            MATCH (m:Materia)
            OPTIONAL MATCH (e:Estudiante {id: $id_estudiante})-[rel:ANOTADO_EN]->(m)
            RETURN m.id AS id,
                   m.nombre AS nombre,
                   m.descripcion AS descripcion,
                   m.nivel_dificultad AS nivel_dificultad,
                   m.tiempo_estimado AS tiempo_estimado,
                   m.frecuencia_uso AS frecuencia_uso,
                   CASE
                     WHEN rel IS NULL THEN 'no_cursada'
                     WHEN rel.completado = true THEN 'aprobada'
                     ELSE 'cursando'
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

    def set_studied(self, id_estudiante: str, id_recurso: str, completado: bool) -> None:
        query = """
            MATCH (e:Estudiante {id: $id_estudiante}), (r:Recurso {id: $id_recurso})
            CREATE (e)-[:ESTUDIO {
                completado: $completado,
                intentos: 1
            }]->(r)
        """
        params = {"id_estudiante": id_estudiante, "id_recurso": id_recurso, "completado": completado}
        print(f"[Neo4j] WRITE {query.strip()}\n       params={params}")
        self._neo4j.write(query, **params)

    def set_completed(self, id_estudiante: str, id_actividad: str,
                      aprobado: bool, puntaje: float) -> None:
        query = """
            MATCH (e:Estudiante {id: $id_estudiante}), (a:Actividad {id: $id_actividad})
            CREATE (e)-[:COMPLETO {
                aprobado: $aprobado,
                puntaje: $puntaje,
                intentos: 1
            }]->(a)
        """
        params = {"id_estudiante": id_estudiante, "id_actividad": id_actividad,
                  "aprobado": aprobado, "puntaje": puntaje}
        print(f"[Neo4j] WRITE {query.strip()}\n       params={params}")
        self._neo4j.write(query, **params)

    def set_enrollment_completed(self, id_estudiante: str, id_materia: str) -> None:
        query = """
            MATCH (e:Estudiante {id: $id_estudiante})-[rel:ANOTADO_EN]->(m:Materia {id: $id_materia})
            SET rel.completado = true, rel.fecha_fin = datetime()
        """
        params = {"id_estudiante": id_estudiante, "id_materia": id_materia}
        print(f"[Neo4j] WRITE {query.strip()}\n       params={params}")
        self._neo4j.write(query, **params)

    def is_terminado(self, id_estudiante: str, id_recurso: str) -> bool:
        query = """
            MATCH (e:Estudiante {id: $id_estudiante})-[rel:ESTUDIO]->(r:Recurso {id: $id_recurso})
            RETURN rel.completado AS completado
        """
        params = {"id_estudiante": id_estudiante, "id_recurso": id_recurso}
        print(f"[Neo4j] READ {query.strip()}\n       params={params}")
        resultados = self._neo4j.read(query, **params)
        return resultados[0]["completado"] if resultados else False

    def is_aprobado(self, id_estudiante: str, id_actividad: str) -> bool:
        query = """
            MATCH (e:Estudiante {id: $id_estudiante})-[rel:COMPLETO]->(a:Actividad {id: $id_actividad})
            RETURN rel.aprobado AS aprobado
        """
        params = {"id_estudiante": id_estudiante, "id_actividad": id_actividad}
        print(f"[Neo4j] READ {query.strip()}\n       params={params}")
        resultados = self._neo4j.read(query, **params)
        return resultados[0]["aprobado"] if resultados else False
