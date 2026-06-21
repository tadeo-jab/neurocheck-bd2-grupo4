from src.db.neo4j import Neo4jService
from src.model.node_models import Materia


class MateriaRepository:
    """Repository for (:Materia) nodes and their relationships."""

    def __init__(self, neo4j: Neo4jService):
        self._neo4j = neo4j

    def get_materia(self, id: str) -> Materia | None:
        query = "MATCH (m:Materia {id: $id}) RETURN m"
        params = {"id": id}
        print(f"[Neo4j] READ {query}\n       params={params}")
        resultados = self._neo4j.read(query, **params)
        return Materia(**resultados[0]["m"]) if resultados else None

    def exists_by_id(self, id: str) -> bool:
        query = "MATCH (m:Materia {id: $id}) RETURN COUNT(m) > 0 AS existe"
        params = {"id": id}
        print(f"[Neo4j] READ {query}\n       params={params}")
        return self._neo4j.read(query, **params)[0]["existe"]

    def get_all_subjects(self) -> list[Materia]:
        query = "MATCH (m:Materia) RETURN m"
        params = {}
        print(f"[Neo4j] READ {query}")
        resultados = self._neo4j.read(query)
        return [Materia(**r["m"]) for r in resultados]

    def get_all_subject_edges(self) -> list[dict]:
        query = """
            MATCH (a:Materia)-[r:REQUIERE|ALTERNATIVA]->(b:Materia)
            RETURN a.id AS source,
                   b.id AS target,
                   type(r) AS tipo,
                   properties(r) AS propiedades
        """
        print(f"[Neo4j] READ {query.strip()}")
        return self._neo4j.read(query)

    def get_related_subjects(self, id_materia: str) -> list[Materia]:
        query = """
            MATCH (m:Materia {id: $id_materia})
            MATCH (m)-[:REQUIERE|ALTERNATIVA*0..2]-(relacionada:Materia)
            RETURN DISTINCT relacionada
        """
        params = {"id_materia": id_materia}
        print(f"[Neo4j] READ {query.strip()}\n       params={params}")
        resultados = self._neo4j.read(query, **params)
        return [Materia(**r["relacionada"]) for r in resultados]

    def get_prequel_if_exists(self, id_materia: str) -> Materia | None:
        query = """
            MATCH (m:Materia {id: $id})-[:REQUIERE {secuela: true}]->(precuela:Materia)
            RETURN precuela
        """
        params = {"id": id_materia}
        print(f"[Neo4j] READ {query.strip()}\n       params={params}")
        resultados = self._neo4j.read(query, **params)
        return Materia(**resultados[0]["precuela"]) if resultados else None

    def get_passed_count(self, id_estudiante: str) -> int:
        query = """
            MATCH (e:Estudiante {id: $id_estudiante})-[rel:ANOTADO_EN]->(m:Materia)
            WHERE rel.completado = true
            RETURN COUNT(m) AS aprobadas
        """
        params = {"id_estudiante": id_estudiante}
        print(f"[Neo4j] READ {query.strip()}\n       params={params}")
        return self._neo4j.read(query, **params)[0]["aprobadas"]

    def create_subject(self, id: str, nombre: str, descripcion: str,
                       nivel_dificultad: float, tiempo_estimado: int,
                       frecuencia_uso: str) -> None:
        query = """
            CREATE (:Materia {
                id: $id,
                nombre: $nombre,
                descripcion: $descripcion,
                nivel_dificultad: $nivel_dificultad,
                tiempo_estimado: $tiempo_estimado,
                frecuencia_uso: $frecuencia_uso
            })
        """
        params = {"id": id, "nombre": nombre, "descripcion": descripcion,
                  "nivel_dificultad": nivel_dificultad, "tiempo_estimado": tiempo_estimado,
                  "frecuencia_uso": frecuencia_uso}
        print(f"[Neo4j] WRITE {query.strip()}\n       params={params}")
        self._neo4j.write(query, **params)

    def create_requires_relationship(self, origen: str, destino: str,
                                     peso: float, obligatorio: bool,
                                     secuela: bool) -> None:
        query = """
            MATCH (a:Materia {id: $origen}), (b:Materia {id: $destino})
            CREATE (a)-[:REQUIERE {
                peso: $peso,
                obligatorio: $obligatorio,
                secuela: $secuela
            }]->(b)
        """
        params = {"origen": origen, "destino": destino, "peso": peso,
                  "obligatorio": obligatorio, "secuela": secuela}
        print(f"[Neo4j] WRITE {query.strip()}\n       params={params}")
        self._neo4j.write(query, **params)

    def get_related_edges(self, id_materia: str) -> list[dict]:
        query = """
            MATCH (m:Materia {id: $id_materia})
            MATCH (a:Materia)-[r:REQUIERE|ALTERNATIVA]->(b:Materia)
            WHERE (m)-[:REQUIERE|ALTERNATIVA*0..2]-(a)
              AND (m)-[:REQUIERE|ALTERNATIVA*0..2]-(b)
            RETURN DISTINCT a.id AS source,
                            b.id AS target,
                            type(r) AS tipo,
                            properties(r) AS propiedades
        """
        params = {"id_materia": id_materia}
        print(f"[Neo4j] READ {query.strip()}\n       params={params}")
        return self._neo4j.read(query, **params)
