from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

from mongo_service import MongoService
from neo4j_service import Neo4jService

# =============================================================================
# Motor Adaptativo
# =============================================================================


class MotorAdaptativo:
    """Reglas simples de decision que integran MongoDB y Neo4j."""

    def __init__(self, mongo: MongoService, neo4j: Neo4jService) -> None:
        self._mongo = mongo
        self._neo4j = neo4j

    # Regla 1 — Necesidad de refuerzo conceptual
    def evaluar_refuerzo(self, id_usuario: int, tema: str) -> dict[str, Any] | None:
        eventos = self._mongo.detect_difficulties(id_usuario=id_usuario, tema=tema)
        if not eventos:
            return None

        prereqs = self._neo4j.get_prerequisites(tema)
        return {
            "regla": "refuerzo_conceptual",
            "mensaje": f"Se recomienda revisar contenidos prerrequisitos antes de continuar con '{tema}'.",
            "prerrequisitos": [p["tema"] for p in prereqs],
            "eventos_detectados": len(eventos),
        }

    # Regla 2 — Avance de dificultad
    def evaluar_avance(self, id_usuario: int) -> dict[str, Any] | None:
        eventos = self._mongo.get_recent_events(id_usuario, limit=15)
        if len(eventos) < 3:
            return None

        ultimos = eventos[:5]
        alto_rendimiento = all(
            e.get("porcentaje_aciertos", 0) > 85 for e in ultimos if "porcentaje_aciertos" in e
        )
        if not alto_rendimiento:
            return None

        aciertos_consecutivos = 0
        for e in eventos:
            if e.get("porcentaje_aciertos", 0) > 85:
                aciertos_consecutivos += 1
                if aciertos_consecutivos >= 3:
                    break
            else:
                aciertos_consecutivos = 0

        if aciertos_consecutivos < 3:
            return None

        return {
            "regla": "avance_dificultad",
            "mensaje": "Se recomienda avanzar hacia actividades de mayor dificultad.",
            "actividades_aprobadas_consecutivas": aciertos_consecutivos,
        }

    # Regla 3 — Riesgo de abandono
    def evaluar_abandono(self, id_usuario: int) -> dict[str, Any] | None:
        eventos = self._mongo.get_recent_events(id_usuario, limit=30)
        if len(eventos) < 5:
            return None

        abandonos = sum(1 for e in eventos if e.get("estado") == "abandonado")
        ratio_abandono = abandonos / len(eventos)

        if ratio_abandono >= 0.3:
            return {
                "regla": "riesgo_abandono",
                "mensaje": "Se sugiere priorizar recursos breves y formatos alternativos.",
                "ratio_abandono": round(ratio_abandono, 2),
            }
        return None

    # Regla de preferencia de formato
    def evaluar_preferencia_formato(self, id_usuario: int) -> dict[str, Any] | None:
        eventos = self._mongo.get_recent_events(id_usuario, limit=50)
        formatos: dict[str, list[float]] = {}
        for e in eventos:
            fmt = e.get("formato", "lectura")
            if "porcentaje_aciertos" in e:
                formatos.setdefault(fmt, []).append(e["porcentaje_aciertos"])

        if not formatos:
            return None

        promedios = {f: sum(v) / len(v) for f, v in formatos.items() if len(v) >= 2}
        if not promedios:
            return None

        mejor_formato = max(promedios, key=promedios.__getitem__)
        return {
            "regla": "preferencia_formato",
            "mensaje": f"El formato '{mejor_formato}' muestra mejores resultados.",
            "formato_recomendado": mejor_formato,
            "promedios": promedios,
        }

    def evaluar_estudiante(self, id_usuario: int, tema_actual: str) -> list[dict[str, Any]]:
        """Ejecuta todas las reglas adaptativas para un estudiante."""
        recomendaciones: list[dict[str, Any]] = []

        refuerzo = self.evaluar_refuerzo(id_usuario, tema_actual)
        if refuerzo:
            recomendaciones.append(refuerzo)

        avance = self.evaluar_avance(id_usuario)
        if avance:
            recomendaciones.append(avance)

        abandono = self.evaluar_abandono(id_usuario)
        if abandono:
            recomendaciones.append(abandono)

        formato = self.evaluar_preferencia_formato(id_usuario)
        if formato:
            recomendaciones.append(formato)

        return recomendaciones


# =============================================================================
# Datos de semilla (MVP — simulados y acotados)
# =============================================================================

MATERIA = "Introducción a Bases de Datos NoSQL"

TEMAS = [
    {"id": "t1", "nombre": "Modelado de Datos", "descripcion": "Fundamentos conceptuales del modelado de datos.", "nivel_dificultad": 0.3, "tiempo_estimado_minutos": 120, "frecuencia_uso": 5},
    {"id": "t2", "nombre": "Modelo Documental", "descripcion": "Bases de datos documentales y su aplicación.", "nivel_dificultad": 0.43, "tiempo_estimado_minutos": 150, "frecuencia_uso": 4},
    {"id": "t3", "nombre": "Modelo de Grafos", "descripcion": "Bases de datos orientadas a grafos.", "nivel_dificultad": 0.67, "tiempo_estimado_minutos": 120, "frecuencia_uso": 2},
    {"id": "t4", "nombre": "Escalabilidad Horizontal", "descripcion": "Estrategias de escalabilidad en NoSQL.", "nivel_dificultad": 0.7, "tiempo_estimado_minutos": 100, "frecuencia_uso": 1},
    {"id": "t5", "nombre": "Modelo NoSQL", "descripcion": "Panorama general de modelos NoSQL.", "nivel_dificultad": 0.5, "tiempo_estimado_minutos": 90, "frecuencia_uso": 3},
    {"id": "t6", "nombre": "Consultas Cypher", "descripcion": "Lenguaje de consultas para grafos.", "nivel_dificultad": 0.55, "tiempo_estimado_minutos": 140, "frecuencia_uso": 2},
    {"id": "t7", "nombre": "Agregaciones en MongoDB", "descripcion": "Pipeline de agregación documental.", "nivel_dificultad": 0.6, "tiempo_estimado_minutos": 130, "frecuencia_uso": 3},
]

ACTIVIDADES = [
    {"id": "a1", "nombre": "Lectura: Fundamentos de Modelado", "descripcion": "Lectura introductoria sobre fundamentos del modelado de datos.", "tipo": "lectura", "dificultad": 0.2, "tiempo_estimado_minutos": 30, "carga_cognitiva": 0.3, "puntaje_maximo": 10},
    {"id": "a2", "nombre": "Quiz Modelado de Datos", "descripcion": "Cuestionario de evaluación sobre modelado de datos.", "tipo": "cuestionario", "dificultad": 0.3, "tiempo_estimado_minutos": 20, "carga_cognitiva": 0.5, "puntaje_maximo": 100},
    {"id": "a3", "nombre": "Video: Modelo Documental", "descripcion": "Video explicativo sobre bases de datos documentales.", "tipo": "video", "dificultad": 0.3, "tiempo_estimado_minutos": 25, "carga_cognitiva": 0.3, "puntaje_maximo": 10},
    {"id": "a4", "nombre": "Quiz MongoDB", "descripcion": "Cuestionario sobre conceptos de MongoDB.", "tipo": "cuestionario", "dificultad": 0.4, "tiempo_estimado_minutos": 25, "carga_cognitiva": 0.55, "puntaje_maximo": 100},
    {"id": "a5", "nombre": "Ejercicio: Modelado Documental", "descripcion": "Ejercicio práctico de modelado documental.", "tipo": "ejercicio", "dificultad": 0.5, "tiempo_estimado_minutos": 45, "carga_cognitiva": 0.6, "puntaje_maximo": 100},
    {"id": "a6", "nombre": "Lectura: Grafos", "descripcion": "Lectura sobre fundamentos de bases de datos de grafos.", "tipo": "lectura", "dificultad": 0.5, "tiempo_estimado_minutos": 35, "carga_cognitiva": 0.5, "puntaje_maximo": 10},
    {"id": "a7", "nombre": "Quiz Modelo de Grafos", "descripcion": "Cuestionario de evaluación sobre modelo de grafos.", "tipo": "cuestionario", "dificultad": 0.65, "tiempo_estimado_minutos": 30, "carga_cognitiva": 0.7, "puntaje_maximo": 100},
    {"id": "a8", "nombre": "Ejercicio Grafos Nivel Avanzado", "descripcion": "Ejercicio avanzado de modelado con grafos.", "tipo": "ejercicio", "dificultad": 0.8, "tiempo_estimado_minutos": 60, "carga_cognitiva": 0.85, "puntaje_maximo": 100},
    {"id": "a9", "nombre": "Proyecto: Modelado NoSQL Integrador", "descripcion": "Proyecto integrador que combina múltiples modelos NoSQL.", "tipo": "proyecto", "dificultad": 0.75, "tiempo_estimado_minutos": 120, "carga_cognitiva": 0.8, "puntaje_maximo": 100},
    {"id": "a10", "nombre": "Video: Escalabilidad", "descripcion": "Video sobre estrategias de escalabilidad horizontal.", "tipo": "video", "dificultad": 0.55, "tiempo_estimado_minutos": 20, "carga_cognitiva": 0.4, "puntaje_maximo": 10},
    {"id": "a11", "nombre": "Quiz Escalabilidad Horizontal", "descripcion": "Cuestionario sobre escalabilidad en bases de datos.", "tipo": "cuestionario", "dificultad": 0.7, "tiempo_estimado_minutos": 25, "carga_cognitiva": 0.7, "puntaje_maximo": 100},
    {"id": "a12", "nombre": "Laboratorio: Agregaciones", "descripcion": "Laboratorio práctico de pipeline de agregación.", "tipo": "laboratorio", "dificultad": 0.6, "tiempo_estimado_minutos": 60, "carga_cognitiva": 0.65, "puntaje_maximo": 100},
    {"id": "a13", "nombre": "Quiz Consultas Cypher", "descripcion": "Cuestionario sobre lenguaje de consultas Cypher.", "tipo": "cuestionario", "dificultad": 0.55, "tiempo_estimado_minutos": 25, "carga_cognitiva": 0.6, "puntaje_maximo": 100},
    {"id": "a14", "nombre": "Lectura: Agregaciones", "descripcion": "Lectura sobre el pipeline de agregación en MongoDB.", "tipo": "lectura", "dificultad": 0.45, "tiempo_estimado_minutos": 30, "carga_cognitiva": 0.45, "puntaje_maximo": 10},
    {"id": "a15", "nombre": "Ejercicio: Cypher Básico", "descripcion": "Ejercicio introductorio de consultas Cypher.", "tipo": "ejercicio", "dificultad": 0.5, "tiempo_estimado_minutos": 40, "carga_cognitiva": 0.55, "puntaje_maximo": 100},
]

RECURSOS = [
    {"id": "r1", "tipo": "lectura", "duracion": 30, "carga_cognitiva": 0.3, "url": "/recursos/modelado-datos.pdf", "estilo_aprendizaje_optimo": ["secuencial"]},
    {"id": "r2", "tipo": "video", "duracion": 25, "carga_cognitiva": 0.3, "url": "/recursos/modelo-documental.mp4", "estilo_aprendizaje_optimo": ["visual", "secuencial"]},
    {"id": "r3", "tipo": "lectura", "duracion": 35, "carga_cognitiva": 0.5, "url": "/recursos/grafos.pdf", "estilo_aprendizaje_optimo": ["secuencial"]},
    {"id": "r4", "tipo": "video", "duracion": 20, "carga_cognitiva": 0.4, "url": "/recursos/escalabilidad.mp4", "estilo_aprendizaje_optimo": ["visual"]},
    {"id": "r5", "tipo": "ejercicio-interactivo", "duracion": 45, "carga_cognitiva": 0.6, "url": "/recursos/ej-modelado-doc.html", "estilo_aprendizaje_optimo": ["practico", "kinestetico"]},
    {"id": "r6", "tipo": "lectura", "duracion": 30, "carga_cognitiva": 0.45, "url": "/recursos/agregaciones.pdf", "estilo_aprendizaje_optimo": ["secuencial"]},
    {"id": "r7", "tipo": "video", "duracion": 25, "carga_cognitiva": 0.5, "url": "/recursos/cypher.mp4", "estilo_aprendizaje_optimo": ["visual", "practico"]},
    {"id": "r8", "tipo": "ejercicio-interactivo", "duracion": 40, "carga_cognitiva": 0.55, "url": "/recursos/ej-cypher.html", "estilo_aprendizaje_optimo": ["practico", "kinestetico"]},
]

ESTILOS = ["visual", "secuencial", "practico", "kinestetico"]
FORMATOS = ["lectura", "video", "ejercicio", "cuestionario", "laboratorio", "proyecto"]
TIPOS_EVENTO = ["lectura_contenido", "quiz_resuelto", "ejercicio_resuelto", "video_visto", "abandono_actividad", "avance_tema", "actividad_repaso"]


def _random_date(start: datetime, end: datetime) -> str:
    delta = end - start
    random_delta = timedelta(seconds=random.randint(0, int(delta.total_seconds())))
    return (start + random_delta).strftime("%Y-%m-%dT%H:%M:%S")


def seed_mongo(mongo: MongoService, n_estudiantes: int = 40) -> list[int]:
    """Populate MongoDB with simulated students, sessions, and events."""
    mongo.collection("estudiantes").drop()
    mongo.collection("sesiones_estudio").drop()
    mongo.collection("eventos_interaccion").drop()
    estudiante_ids = list(range(1, n_estudiantes + 1))

    # --- estudiantes ---
    docs_estudiantes: list[dict[str, Any]] = []
    for eid in estudiante_ids:
        docs_estudiantes.append({
            "_id": eid,
            "nombre": f"Estudiante {eid:03d}",
            "objetivos": random.sample(
                ["Aprender MongoDB", "Comprender Grafos", "Dominar NoSQL", "Modelar Datos", "Escalar BD"], k=2
            ),
            "preferencias": {
                "formato": random.choice(FORMATOS[:3]),
                "horario": random.choice(["mañana", "tarde", "noche"]),
            },
            "metricas": {
                "fatiga": round(random.uniform(0.1, 0.5), 2),
                "atencion": round(random.uniform(0.5, 1.0), 2),
            },
            "progreso": {
                "temasCompletados": random.randint(0, len(TEMAS)),
                "nivelActual": random.choice(["basico", "intermedio", "avanzado"]),
            },
        })
    mongo.collection("estudiantes").insert_many(docs_estudiantes)

    # --- sesiones_estudio ---
    base = datetime(2026, 5, 1)
    sesiones_docs: list[dict[str, Any]] = []
    for eid in estudiante_ids:
        n_sesiones = random.randint(5, 20)
        for s in range(n_sesiones):
            sesiones_docs.append({
                "id_sesion": f"ses_{eid:03d}_{s:03d}",
                "id_usuario": eid,
                "fecha": _random_date(base, base + timedelta(days=30)),
                "actividad": random.choice([a["nombre"] for a in ACTIVIDADES]),
                "tema": random.choice([t["nombre"] for t in TEMAS]),
                "duracion": random.randint(10, 90),
                "intentos": random.randint(1, 5),
                "porcentaje_aciertos": random.randint(30, 100),
            })
    mongo.collection("sesiones_estudio").insert_many(sesiones_docs)

    # --- eventos_interaccion ---
    eventos_docs: list[dict[str, Any]] = []
    for _ in range(800):
        eid = random.choice(estudiante_ids)
        tipo = random.choice(TIPOS_EVENTO)
        tema_elegido = random.choice(TEMAS)
        actividad_elegida = random.choice(ACTIVIDADES)
        sesion_id = f"ses_{eid:03d}_{random.randint(0, 19):03d}"

        evento: dict[str, Any] = {
            "id_evento": f"evt_{random.randint(1000, 9999)}",
            "id_usuario": eid,
            "id_sesion": sesion_id,
            "tipo_evento": tipo,
            "tema": tema_elegido["nombre"],
            "actividad": actividad_elegida["nombre"],
            "dificultad": actividad_elegida["dificultad"],
            "timestamp": _random_date(base, base + timedelta(days=30)),
            "duracion_minutos": random.randint(2, 60),
        }

        if tipo == "quiz_resuelto":
            aciertos = random.randint(0, 10)
            errores = 10 - aciertos
            evento.update({
                "intentos": random.randint(1, 5),
                "aciertos": aciertos,
                "errores": errores,
                "porcentaje_aciertos": aciertos * 10,
                "estado": "completado",
                "formato": "cuestionario",
            })
        elif tipo == "ejercicio_resuelto":
            aciertos = random.randint(0, 10)
            evento.update({
                "intentos": random.randint(1, 4),
                "aciertos": aciertos,
                "errores": 10 - aciertos,
                "porcentaje_aciertos": aciertos * 10,
                "estado": "completado",
                "formato": "ejercicio",
            })
        elif tipo == "abandono_actividad":
            evento["estado"] = "abandonado"
            evento["formato"] = random.choice(["ejercicio", "cuestionario", "lectura"])
        elif tipo == "lectura_contenido":
            evento["estado"] = "completado"
            evento["formato"] = "lectura"
        elif tipo == "video_visto":
            evento["estado"] = "completado"
            evento["formato"] = "video"

        eventos_docs.append(evento)
    mongo.collection("eventos_interaccion").insert_many(eventos_docs)
    mongo.create_indexes()

    return estudiante_ids


def seed_neo4j(neo4j: Neo4jService, estudiante_ids: list[int]) -> None:
    """Populate Neo4j with the conceptual knowledge graph."""
    neo4j.write("MATCH (n) DETACH DELETE n")
    neo4j.create_indexes()
    neo4j.create_constraints()

    # Materia
    neo4j.create_materia({"id": "m1", "nombre": MATERIA, "nivel_dificultad": 0.55})

    # Temas
    for t in TEMAS:
        neo4j.create_tema(t)

    # Actividades
    for a in ACTIVIDADES:
        neo4j.create_actividad(a)

    # Recursos
    for r in RECURSOS:
        neo4j.create_recurso(r)

    # Estudiantes (subset in Neo4j for graph queries)
    for eid in estudiante_ids[:15]:
        neo4j.create_estudiante({
            "id": str(eid),
            "nivel_maestria_promedio": round(random.uniform(0.3, 0.9), 2),
            "estilo_preferido": random.choice(ESTILOS),
            "sesion_actual": f"ses_{eid:03d}_{random.randint(0, 19):03d}",
        })

    # Sesiones
    for eid in estudiante_ids[:15]:
        for s in range(3):
            neo4j.create_sesion({
                "id": f"ses_{eid:03d}_{s:03d}",
                "inicio": _random_date(datetime(2026, 5, 1), datetime(2026, 5, 30)),
                "final": _random_date(datetime(2026, 5, 1), datetime(2026, 5, 30)),
            })

    # -- Relaciones conceptuales entre temas ---

    # REQUIERE: Modelo de Grafos → Modelo NoSQL → Modelado de Datos
    neo4j.relate_requiere("t3", "t5", {"peso": 0.85, "observaciones": "Conceptos fundamentales de NoSQL necesarios", "nivel": "obligatorio"})
    neo4j.relate_requiere("t5", "t1", {"peso": 0.9, "observaciones": "Modelado de datos es base para entender NoSQL", "nivel": "obligatorio"})
    neo4j.relate_requiere("t2", "t1", {"peso": 0.7, "observaciones": "Fundamentos de modelado necesarios", "nivel": "obligatorio"})
    neo4j.relate_requiere("t6", "t3", {"peso": 0.8, "observaciones": "Requiere comprender grafos primero", "nivel": "obligatorio"})
    neo4j.relate_requiere("t7", "t2", {"peso": 0.75, "observaciones": "Requiere comprender modelo documental", "nivel": "obligatorio"})
    neo4j.relate_requiere("t4", "t5", {"peso": 0.6, "observaciones": "Conceptos NoSQL como base", "nivel": "recomendado"})

    # CORRELACIONA
    neo4j.relate_correlaciona("t2", "t7", {"fuerza": 0.9})
    neo4j.relate_correlaciona("t3", "t6", {"fuerza": 0.95})
    neo4j.relate_correlaciona("t1", "t5", {"fuerza": 0.7})

    # ALTERNATIVA
    neo4j.relate_alternativa("t4", "t2", {"costo_adicional": 0.3, "estilo_favorecido": "practico"})

    # PROFUNDIZA
    neo4j.relate_profundiza("t2", "t1", {"factor_complejidad": 1.4})
    neo4j.relate_profundiza("t3", "t5", {"factor_complejidad": 1.3})

    # PERTENECE_A
    neo4j.relate_pertenece_a("t1", "m1", {"peso_en_materia": 1.0})
    neo4j.relate_pertenece_a("t2", "m1", {"peso_en_materia": 0.9})
    neo4j.relate_pertenece_a("t3", "m1", {"peso_en_materia": 0.9})
    neo4j.relate_pertenece_a("t4", "m1", {"peso_en_materia": 0.7})
    neo4j.relate_pertenece_a("t5", "m1", {"peso_en_materia": 0.8})
    neo4j.relate_pertenece_a("t6", "m1", {"peso_en_materia": 0.6})
    neo4j.relate_pertenece_a("t7", "m1", {"peso_en_materia": 0.7})

    # EVALUA
    neo4j.relate_evalua("a1", "t1", {"cobertura": 0.5, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a2", "t1", {"cobertura": 1.0, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a3", "t2", {"cobertura": 0.4, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a4", "t2", {"cobertura": 0.5, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a5", "t2", {"cobertura": 1.0, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a6", "t3", {"cobertura": 0.5, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a7", "t3", {"cobertura": 0.6, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a8", "t3", {"cobertura": 1.0, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a10", "t4", {"cobertura": 0.5, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a11", "t4", {"cobertura": 1.0, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a12", "t7", {"cobertura": 1.0, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a13", "t6", {"cobertura": 0.6, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a14", "t7", {"cobertura": 0.5, "umbral_aprobacion": 0.7})
    neo4j.relate_evalua("a15", "t6", {"cobertura": 1.0, "umbral_aprobacion": 0.7})

    # EXPLICA
    neo4j.relate_explica("r1", "t1", {"cobertura": 1.0})
    neo4j.relate_explica("r2", "t2", {"cobertura": 0.6})
    neo4j.relate_explica("r3", "t3", {"cobertura": 0.7})
    neo4j.relate_explica("r4", "t4", {"cobertura": 0.6})
    neo4j.relate_explica("r5", "t2", {"cobertura": 0.8})
    neo4j.relate_explica("r6", "t7", {"cobertura": 0.7})
    neo4j.relate_explica("r7", "t6", {"cobertura": 0.6})
    neo4j.relate_explica("r8", "t6", {"cobertura": 0.9})

    # -- Relaciones estudiante-contenido ---

    for eid in estudiante_ids[:15]:
        temas_estudiados = random.sample(TEMAS, k=random.randint(2, len(TEMAS)))
        for tema in temas_estudiados:
            base_date = _random_date(datetime(2026, 5, 1), datetime(2026, 5, 28))
            neo4j.relate_estudio(str(eid), tema["id"], {
                "tiempo_total_minutos": random.randint(20, 200),
                "fecha": base_date,
                "veces_estudiado": random.randint(1, 5),
                "nivel_alcanzado": round(random.uniform(0.3, 0.95), 2),
            })

        actividades_completadas = random.sample(ACTIVIDADES, k=random.randint(2, 8))
        for act in actividades_completadas:
            neo4j.relate_completo(str(eid), act["id"], {
                "puntaje_obtenido": random.randint(40, 100),
                "tiempo_tomado_segundos": random.randint(600, 5400),
                "fecha_completado": _random_date(datetime(2026, 5, 1), datetime(2026, 5, 30)),
                "intentos": random.randint(1, 4),
                "aprobado": random.choice([True, False]),
            })

        for s in range(3):
            neo4j.relate_sesion(str(eid), f"ses_{eid:03d}_{s:03d}", {
                "duracion_real": random.randint(10, 120),
            })


# =============================================================================
# Demo
# =============================================================================


def demo() -> None:
    print("=" * 60)
    print("  NeuroCheck — Motor de Aprendizaje Adaptativo (MVP)")
    print("=" * 60)

    mongo = MongoService()
    neo4j = Neo4jService()
    motor = MotorAdaptativo(mongo, neo4j)

    with mongo.session():
        print("\n[1/7] Insertando datos simulados en MongoDB...")
        ids = seed_mongo(mongo)
        print(f"      {len(ids)} estudiantes, sesiones y ~800 eventos cargados.")

        print("\n[2/7] Insertando grafo de conocimiento en Neo4j...")
        seed_neo4j(neo4j, ids)
        print("      Nodos y relaciones creados en Neo4j.")

        # -- Demostracion de consultas --

        test_id = random.choice(ids)

        print(f"\n[3/7] Perfil completo del estudiante {test_id} (Consulta 1):")
        perfil = mongo.get_student_profile(test_id)
        if perfil:
            print(f"      Nombre: {perfil['nombre']}")
            print(f"      Objetivos: {perfil['objetivos']}")
            print(f"      Preferencias: {perfil['preferencias']}")
            print(f"      Progreso: {perfil['progreso']}")

        print(f"\n[4/7] Eventos recientes del estudiante {test_id} (Consulta 4):")
        eventos = mongo.get_recent_events(test_id, limit=5)
        for evt in eventos:
            print(f"      {evt['timestamp']} | {evt['tipo_evento']} | {evt.get('tema','')} | estado={evt.get('estado','?')}")

        print(f"\n[5/7] Prerrequisitos de 'Modelo de Grafos' (Consulta 5):")
        prereqs = neo4j.get_prerequisites("Modelo de Grafos")
        for p in prereqs:
            print(f"      → {p['tema']} (dificultad: {p['dificultad']})")

        print(f"\n[6/7] Motor Adaptativo — evaluando estudiante {test_id}:")
        recomendaciones = motor.evaluar_estudiante(test_id, "Modelo de Grafos")
        if recomendaciones:
            for rec in recomendaciones:
                print(f"      [{rec['regla']}] {rec['mensaje']}")
        else:
            print("      Sin recomendaciones — rendimiento dentro de lo esperado.")

        print(f"\n[7/7] Temas con mayor dificultad (consulta analitica):")
        dificultades = mongo.topics_by_difficulty()
        for d in dificultades[:5]:
            print(f"      {d['_id']}: {d['promedio_aciertos']:.1f}% aciertos ({d['cantidad']} quizzes)")

    print("\n" + "=" * 60)
    print("  Demo completada.")
    print("=" * 60)


if __name__ == "__main__":
    demo()
