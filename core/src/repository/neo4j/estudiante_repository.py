from src.db.neo4j import Neo4jService
from src.model.node_models import Estudiante


class EstudianteRepository:
    """Repository for (:Estudiante) nodes in Neo4j."""

    def __init__(self, neo4j: Neo4jService):
        self._neo4j = neo4j

    def get_mate_by_id(self, id: str) -> list[dict]:
        query = """
            MATCH (e:Estudiante {id: $id})-[rel:COMPAÑERO_DE]-(compañero:Estudiante)
            OPTIONAL MATCH (e)-[:ESTUDIO_CON]-(compañero)
            RETURN compañero,
                   rel.solicitud_aceptada AS aceptado,
                   COUNT(*) AS estudios_compartidos
            ORDER BY estudios_compartidos DESC
        """
        resultados = self._neo4j.read(query, id=id)
        return [
            {"estudiante": Estudiante(**r["compañero"]), "aceptado": r["aceptado"]}
            for r in resultados
        ]

    def crear(self, id: str, nombre: str, estilo_preferido: str) -> None:
        query = """
            CREATE (:Estudiante {
                id: $id,
                nombre: $nombre,
                estilo_preferido: $estilo_preferido
            })
        """
        self._neo4j.write(query, id=id, nombre=nombre, estilo_preferido=estilo_preferido)

    def exists_by_id(self, id: str) -> bool:
        query = "MATCH (e:Estudiante {id: $id}) RETURN COUNT(e) > 0 AS existe"
        return self._neo4j.read(query, id=id)[0]["existe"]

    def request_mate(self, id_a: str, id_b: str) -> None:
        query = """
            MATCH (a:Estudiante {id: $id_a}), (b:Estudiante {id: $id_b})
            MERGE (a)-[:COMPAÑERO_DE {solicitud_aceptada: false, fecha_desde: null}]-(b)
        """
        self._neo4j.write(query, id_a=id_a, id_b=id_b)

    def recommend_mates(self, id: str, limite: int = 10) -> list[dict]:
        query = """
            MATCH (e:Estudiante {id: $id})
            MATCH (candidato:Estudiante)
            WHERE candidato <> e
              AND NOT (e)-[:COMPAÑERO_DE]-(candidato)

            // 1. Amigos en común (camino A -> B -> C)
            CALL {
              WITH e, candidato
              OPTIONAL MATCH (e)-[:COMPAÑERO_DE]-(intermedio:Estudiante)-[:COMPAÑERO_DE]-(candidato)
              RETURN COUNT(DISTINCT intermedio) AS peso_amigos
            }

            // 2. Materias en común (vía :ANOTADO_EN)
            CALL {
              WITH e, candidato
              OPTIONAL MATCH (e)-[:ANOTADO_EN]->(m:Materia)<-[:ANOTADO_EN]-(candidato)
              RETURN COUNT(DISTINCT m) AS peso_materias
            }

            // 3. Mismo estilo de aprendizaje
            WITH e, candidato, peso_amigos, peso_materias,
                 CASE WHEN candidato.estilo_preferido = e.estilo_preferido THEN 1 ELSE 0 END AS peso_estilo

            RETURN candidato.id AS id,
                   candidato.nombre AS nombre,
                   peso_amigos * 2 + peso_materias * 3 + peso_estilo AS puntaje
            ORDER BY puntaje DESC
            LIMIT $limite
        """
        return self._neo4j.read(query, id=id, limite=limite)