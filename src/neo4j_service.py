from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from neo4j import GraphDatabase, Session


class Neo4jService:
    """Neo4j service for NeuroCheck — grafo de conocimiento y recomendaciones."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "neurocheck",
        database: str = "neo4j",
    ) -> None:
        self._uri = uri
        self._username = username
        self._password = password
        self._database = database
        self._driver: GraphDatabase.driver | None = None

    # -- connection lifecycle -------------------------------------------------

    @property
    def driver(self) -> GraphDatabase.driver:
        if self._driver is None:
            raise RuntimeError("Neo4jService is not connected. Call connect() first.")
        return self._driver

    def connect(self) -> Neo4jService:
        self._driver = GraphDatabase.driver(
            self._uri,
            auth=(self._username, self._password),
        )
        self._driver.verify_connectivity()
        return self

    def disconnect(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def session(self, **kwargs: Any) -> Session:
        return self.driver.session(database=self._database, **kwargs)

    @contextmanager
    def connect_session(self) -> Iterator[Session]:
        self.connect()
        with self.session() as session:
            yield session
        self.disconnect()

    # -- indexes --------------------------------------------------------------

    def create_indexes(self) -> None:
        """Create Cypher indexes for the conceptual model."""
        indexes = [
            "CREATE INDEX tema_nombre IF NOT EXISTS FOR (t:Tema) ON (t.nombre)",
            "CREATE INDEX materia_nombre IF NOT EXISTS FOR (m:Materia) ON (m.nombre)",
            "CREATE INDEX actividad_nombre IF NOT EXISTS FOR (a:Actividad) ON (a.nombre)",
        ]
        with self.connect_session() as session:
            for stmt in indexes:
                session.run(stmt)

    # -- constraints ----------------------------------------------------------

    def create_constraints(self) -> None:
        """Create uniqueness constraints."""
        # Drop standalone index that conflicts with the constraint (from prior runs)
        with self.connect_session() as session:
            session.run("DROP INDEX estudiante_id IF EXISTS")
        constraints = [
            "CREATE CONSTRAINT estudiante_id_unique IF NOT EXISTS FOR (e:Estudiante) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT tema_id_unique IF NOT EXISTS FOR (t:Tema) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT materia_id_unique IF NOT EXISTS FOR (m:Materia) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT actividad_id_unique IF NOT EXISTS FOR (a:Actividad) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT recurso_id_unique IF NOT EXISTS FOR (r:Recurso) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT sesion_id_unique IF NOT EXISTS FOR (s:Sesion) REQUIRE s.id IS UNIQUE",
        ]
        with self.connect_session() as session:
            for stmt in constraints:
                session.run(stmt)

    # -- generic query helpers ------------------------------------------------

    def run(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        with self.connect_session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def write(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        with self.connect_session() as session:
            result = session.execute_write(
                lambda tx: [record.data() for record in tx.run(query, parameters or {})]
            )
            return result

    def read(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        with self.connect_session() as session:
            result = session.execute_read(
                lambda tx: [record.data() for record in tx.run(query, parameters or {})]
            )
            return result

    # -- node creation --------------------------------------------------------

    def create_estudiante(self, properties: dict[str, Any]) -> None:
        self.write(
            """
            MERGE (e:Estudiante {id: $id})
            SET e.nivel_maestria_promedio = $nivel_maestria_promedio,
                e.estilo_preferido = $estilo_preferido,
                e.sesion_actual = $sesion_actual
            """,
            properties,
        )

    def create_tema(self, properties: dict[str, Any]) -> None:
        self.write(
            """
            MERGE (t:Tema {id: $id})
            SET t.nombre = $nombre,
                t.descripcion = $descripcion,
                t.nivel_dificultad = $nivel_dificultad,
                t.tiempo_estimado_minutos = $tiempo_estimado_minutos,
                t.frecuencia_uso = $frecuencia_uso
            """,
            properties,
        )

    def create_materia(self, properties: dict[str, Any]) -> None:
        self.write(
            """
            MERGE (m:Materia {id: $id})
            SET m.nombre = $nombre,
                m.nivel_dificultad = $nivel_dificultad
            """,
            properties,
        )

    def create_actividad(self, properties: dict[str, Any]) -> None:
        self.write(
            """
            MERGE (a:Actividad {id: $id})
            SET a.nombre = $nombre,
                a.descripcion = $descripcion,
                a.tipo = $tipo,
                a.dificultad = $dificultad,
                a.tiempo_estimado_minutos = $tiempo_estimado_minutos,
                a.carga_cognitiva = $carga_cognitiva,
                a.puntaje_maximo = $puntaje_maximo
            """,
            properties,
        )

    def create_recurso(self, properties: dict[str, Any]) -> None:
        self.write(
            """
            MERGE (r:Recurso {id: $id})
            SET r.tipo = $tipo,
                r.duracion = $duracion,
                r.carga_cognitiva = $carga_cognitiva,
                r.url = $url,
                r.estilo_aprendizaje_optimo = $estilo_aprendizaje_optimo
            """,
            properties,
        )

    def create_sesion(self, properties: dict[str, Any]) -> None:
        self.write(
            """
            MERGE (s:Sesion {id: $id})
            SET s.inicio = $inicio,
                s.final = $final
            """,
            properties,
        )

    # -- relationship creation ------------------------------------------------

    def relate_requiere(
        self, tema_origen_id: str, tema_destino_id: str, properties: dict[str, Any]
    ) -> None:
        self.write(
            """
            MATCH (origen:Tema {id: $tema_origen_id})
            MATCH (destino:Tema {id: $tema_destino_id})
            MERGE (origen)-[r:REQUIERE]->(destino)
            SET r.peso = $peso,
                r.observaciones = $observaciones,
                r.nivel = $nivel
            """,
            {"tema_origen_id": tema_origen_id, "tema_destino_id": tema_destino_id, **properties},
        )

    def relate_correlaciona(
        self, tema_a_id: str, tema_b_id: str, properties: dict[str, Any]
    ) -> None:
        self.write(
            """
            MATCH (a:Tema {id: $tema_a_id})
            MATCH (b:Tema {id: $tema_b_id})
            MERGE (a)-[r:CORRELACIONA]->(b)
            SET r.fuerza = $fuerza
            """,
            {"tema_a_id": tema_a_id, "tema_b_id": tema_b_id, **properties},
        )

    def relate_alternativa(
        self, tema_origen_id: str, tema_destino_id: str, properties: dict[str, Any]
    ) -> None:
        self.write(
            """
            MATCH (origen:Tema {id: $tema_origen_id})
            MATCH (destino:Tema {id: $tema_destino_id})
            MERGE (origen)-[r:ALTERNATIVA]->(destino)
            SET r.costo_adicional = $costo_adicional,
                r.estilo_favorecido = $estilo_favorecido
            """,
            {"tema_origen_id": tema_origen_id, "tema_destino_id": tema_destino_id, **properties},
        )

    def relate_profundiza(
        self, tema_avanzado_id: str, tema_base_id: str, properties: dict[str, Any]
    ) -> None:
        self.write(
            """
            MATCH (avanzado:Tema {id: $tema_avanzado_id})
            MATCH (base:Tema {id: $tema_base_id})
            MERGE (avanzado)-[r:PROFUNDIZA]->(base)
            SET r.factor_complejidad = $factor_complejidad
            """,
            {"tema_avanzado_id": tema_avanzado_id, "tema_base_id": tema_base_id, **properties},
        )

    def relate_pertenece_a(
        self, tema_id: str, materia_id: str, properties: dict[str, Any] | None = None
    ) -> None:
        props = properties or {"peso_en_materia": 1.0}
        self.write(
            """
            MATCH (t:Tema {id: $tema_id})
            MATCH (m:Materia {id: $materia_id})
            MERGE (t)-[r:PERTENECE_A]->(m)
            SET r.peso_en_materia = $peso_en_materia
            """,
            {"tema_id": tema_id, "materia_id": materia_id, **props},
        )

    def relate_evalua(
        self, actividad_id: str, tema_id: str, properties: dict[str, Any]
    ) -> None:
        self.write(
            """
            MATCH (a:Actividad {id: $actividad_id})
            MATCH (t:Tema {id: $tema_id})
            MERGE (a)-[r:EVALUA]->(t)
            SET r.cobertura = $cobertura,
                r.umbral_aprobacion = $umbral_aprobacion
            """,
            {"actividad_id": actividad_id, "tema_id": tema_id, **properties},
        )

    def relate_explica(
        self, recurso_id: str, tema_id: str, properties: dict[str, Any]
    ) -> None:
        self.write(
            """
            MATCH (r:Recurso {id: $recurso_id})
            MATCH (t:Tema {id: $tema_id})
            MERGE (r)-[e:EXPLICA]->(t)
            SET e.cobertura = $cobertura
            """,
            {"recurso_id": recurso_id, "tema_id": tema_id, **properties},
        )

    def relate_estudio(
        self, estudiante_id: str, tema_id: str, properties: dict[str, Any]
    ) -> None:
        self.write(
            """
            MATCH (e:Estudiante {id: $estudiante_id})
            MATCH (t:Tema {id: $tema_id})
            MERGE (e)-[r:ESTUDIO]->(t)
            SET r.tiempo_total_minutos = $tiempo_total_minutos,
                r.fecha = $fecha,
                r.veces_estudiado = $veces_estudiado,
                r.nivel_alcanzado = $nivel_alcanzado
            """,
            {"estudiante_id": estudiante_id, "tema_id": tema_id, **properties},
        )

    def relate_completo(
        self, estudiante_id: str, actividad_id: str, properties: dict[str, Any]
    ) -> None:
        self.write(
            """
            MATCH (e:Estudiante {id: $estudiante_id})
            MATCH (a:Actividad {id: $actividad_id})
            MERGE (e)-[r:COMPLETO]->(a)
            SET r.puntaje_obtenido = $puntaje_obtenido,
                r.tiempo_tomado_segundos = $tiempo_tomado_segundos,
                r.fecha_completado = $fecha_completado,
                r.intentos = $intentos,
                r.aprobado = $aprobado
            """,
            {"estudiante_id": estudiante_id, "actividad_id": actividad_id, **properties},
        )

    def relate_sesion(
        self, estudiante_id: str, sesion_id: str, properties: dict[str, Any]
    ) -> None:
        self.write(
            """
            MATCH (e:Estudiante {id: $estudiante_id})
            MATCH (s:Sesion {id: $sesion_id})
            MERGE (e)-[r:PERTENECESE_A_SESION]->(s)
            SET r.duracion_real = $duracion_real
            """,
            {"estudiante_id": estudiante_id, "sesion_id": sesion_id, **properties},
        )

    # -- consultas del dominio ------------------------------------------------

    # Consulta 5 — Encontrar prerrequisitos de un tema
    def get_prerequisites(self, tema_nombre: str) -> list[dict[str, Any]]:
        return self.read(
            """
            MATCH (t:Tema {nombre: $nombre})-[:REQUIERE]->(prereq:Tema)
            RETURN prereq.nombre AS tema,
                   prereq.nivel_dificultad AS dificultad,
                   prereq.tiempo_estimado_minutos AS tiempo_estimado
            """,
            {"nombre": tema_nombre},
        )

    # Consulta 6 — Calcular ruta optima de aprendizaje (shortest path al objetivo)
    def get_optimal_path(
        self, estudiante_id: str, tema_objetivo_nombre: str
    ) -> list[dict[str, Any]]:
        return self.read(
            """
            MATCH (e:Estudiante {id: $estudiante_id})-[:ESTUDIO]->(t_completado:Tema)
            MATCH (t_objetivo:Tema {nombre: $tema_objetivo_nombre})
            MATCH path = shortestPath((t_completado)-[:REQUIERE*..6]->(t_objetivo))
            WITH nodes(path) AS secuencia
            UNWIND secuencia AS nodo
            RETURN nodo.nombre AS tema,
                   nodo.nivel_dificultad AS dificultad,
                   nodo.tiempo_estimado_minutos AS tiempo_estimado
            """,
            {"estudiante_id": estudiante_id, "tema_objetivo_nombre": tema_objetivo_nombre},
        )

    # Consulta 7 — Buscar caminos alternativos de aprendizaje
    def get_alternative_paths(
        self, estudiante_id: str, tema_conflictivo_nombre: str
    ) -> list[dict[str, Any]]:
        return self.read(
            """
            MATCH (e:Estudiante {id: $estudiante_id})-[:ESTUDIO]->(t_completado:Tema)
            MATCH (t_conflicto:Tema {nombre: $tema_conflictivo_nombre})
            MATCH path = (t_completado)-[:ALTERNATIVA|REQUIERE*..6]->(t_conflicto)
            WHERE any(r IN relationships(path) WHERE type(r) = 'ALTERNATIVA')
            WITH nodes(path) AS secuencia, relationships(path) AS rels
            RETURN [n IN secuencia | n.nombre] AS ruta,
                   reduce(costo = 0, r IN rels | costo + coalesce(r.costo_adicional, 0)) AS costo_total
            ORDER BY costo_total ASC
            LIMIT 3
            """,
            {
                "estudiante_id": estudiante_id,
                "tema_conflictivo_nombre": tema_conflictivo_nombre,
            },
        )

    # -- consultas analiticas -------------------------------------------------

    def students_by_topic(self, tema_nombre: str) -> list[dict[str, Any]]:
        """Que estudiantes estudiaron determinado tema."""
        return self.read(
            """
            MATCH (e:Estudiante)-[es:ESTUDIO]->(t:Tema {nombre: $nombre})
            RETURN e.id AS estudiante_id,
                   es.nivel_alcanzado AS nivel,
                   es.veces_estudiado AS repeticiones,
                   es.fecha AS ultima_fecha
            ORDER BY es.nivel_alcanzado ASC
            """,
            {"nombre": tema_nombre},
        )

    def topic_dependency_chain(self, tema_nombre: str) -> list[dict[str, Any]]:
        """Cadena completa de dependencias de un tema (todos los prerrequisitos recursivos)."""
        return self.read(
            """
            MATCH (t:Tema {nombre: $nombre})-[:REQUIERE*1..5]->(prereq:Tema)
            RETURN prereq.nombre AS prerrequisito,
                   prereq.nivel_dificultad AS dificultad
            ORDER BY prereq.nivel_dificultad ASC
            """,
            {"nombre": tema_nombre},
        )
