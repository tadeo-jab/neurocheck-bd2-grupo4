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

    # ── Consulta 5 — Prerrequisitos recursivos ──────────────

    def get_all_prerequisites(self, id_materia: str) -> list[dict]:
        """Devuelve todos los prerrequisitos (directos e indirectos) de una materia."""
        query = """
            MATCH path = (m:Materia {id: $id})-[:REQUIERE*1..]->(req:Materia)
            RETURN DISTINCT req,
                            length(path) AS profundidad
            ORDER BY profundidad ASC
        """
        resultados = self._neo4j.read(query, id=id_materia)
        return [
            {**dict(r["req"]), "profundidad": r["profundidad"]}
            for r in resultados
        ]

    # ── Consulta 6 — Ruta óptima de aprendizaje ────────────

    def get_optimal_learning_path(self, id_estudiante: str,
                                  id_materia_objetivo: str) -> list[dict]:
        """
        Devuelve la secuencia de materias que el estudiante debe cursar
        para llegar al objetivo, excluyendo las que ya completó.
        Ordena por profundidad (más lejanas primero = hay que cursarlas antes).
        """
        query = """
            MATCH path = (objetivo:Materia {id: $id_objetivo})<-[:REQUIERE*0..]-(req:Materia)
            WHERE NOT EXISTS {
                MATCH (:Estudiante {id: $id_est})-[:ANOTADO_EN {completado: true}]->(req)
            }
            RETURN DISTINCT req,
                            length(path) AS distancia
            ORDER BY distancia DESC
        """
        resultados = self._neo4j.read(query,
                                      id_objetivo=id_materia_objetivo,
                                      id_est=id_estudiante)
        return [
            {**dict(r["req"]), "distancia_al_objetivo": r["distancia"]}
            for r in resultados
        ]

    # ── Consulta 7 — Caminos alternativos ──────────────────

    def get_alternative_paths(self, id_materia: str) -> list[dict]:
        """Devuelve materias alternativas para llegar al mismo objetivo."""
        query = """
            MATCH (m:Materia {id: $id})-[r:ALTERNATIVA]->(alt:Materia)
            RETURN alt,
                   r.peso_adicional  AS costo_adicional,
                   r.estilo_favorecido AS estilo_favorecido
        """
        resultados = self._neo4j.read(query, id=id_materia)
        return [
            {
                **dict(r["alt"]),
                "costo_adicional": r["costo_adicional"],
                "estilo_favorecido": r["estilo_favorecido"],
            }
            for r in resultados
        ]



