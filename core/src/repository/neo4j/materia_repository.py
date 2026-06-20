from src.db.neo4j import Neo4jService
from src.model.node_models import Materia


class MateriaRepository:
    """Repository for (:Materia) nodes and their relationships."""

    def __init__(self, neo4j: Neo4jService):
        self._neo4j = neo4j


    def get_materia(self, id: str) -> Materia | None:
        query = "MATCH (m:Materia {id: $id}) RETURN m"
        resultados = self._neo4j.read(query, id=id)
        return Materia(**resultados[0]["m"]) if resultados else None

    def exists_by_id(self, id: str) -> bool:
        query = "MATCH (m:Materia {id: $id}) RETURN COUNT(m) > 0 AS existe"
        return self._neo4j.read(query, id=id)[0]["existe"]

    def get_all_subjects(self) -> list[Materia]:
        query = "MATCH (m:Materia) RETURN m"
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
        return self._neo4j.read(query)

    def get_related_subjects(self, id_materia: str) -> list[Materia]:
        query = """
            MATCH (m:Materia {id: $id_materia})
            MATCH (m)-[:REQUIERE|ALTERNATIVA*0..15]-(relacionada:Materia)
            RETURN DISTINCT relacionada
        """
        resultados = self._neo4j.read(query, id_materia=id_materia)
        return [Materia(**r["relacionada"]) for r in resultados]

    def get_prequel_if_exists(self, id_materia: str) -> Materia | None:
        query = """
            MATCH (m:Materia {id: $id})-[:REQUIERE {secuela: true}]->(precuela:Materia)
            RETURN precuela
        """
        resultados = self._neo4j.read(query, id=id_materia)
        return Materia(**resultados[0]["precuela"]) if resultados else None

    def get_related_edges(self, id_materia: str) -> list[dict]:
        query = """
            MATCH (m:Materia {id: $id_materia})
            MATCH (a:Materia)-[r:REQUIERE|ALTERNATIVA]->(b:Materia)
            WHERE (m)-[:REQUIERE|ALTERNATIVA*0..15]-(a)
              AND (m)-[:REQUIERE|ALTERNATIVA*0..15]-(b)
            RETURN DISTINCT a.id AS source,
                            b.id AS target,
                            type(r) AS tipo,
                            properties(r) AS propiedades
        """
        return self._neo4j.read(query, id_materia=id_materia)
    


