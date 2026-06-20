"""Seed script — populates MongoDB and Neo4j with sample data."""

import uuid
from datetime import datetime, timezone
from pathlib import Path

import bcrypt
import bson

from src.config import settings
from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService

# ═══════════════════════════════════════════════════════════
# Datos semilla
# ═══════════════════════════════════════════════════════════

ESTUDIANTES = [
    {"id": "est-001", "nombre": "Juan Pérez",    "email": "juan@mail.com",   "password": "123456", "estilo": "visual"},
    {"id": "est-002", "nombre": "María Gómez",   "email": "maria@mail.com",  "password": "123456", "estilo": "auditivo"},
    {"id": "est-003", "nombre": "Pedro Ruiz",    "email": "pedro@mail.com",  "password": "123456", "estilo": "kinestésico"},
    {"id": "est-004", "nombre": "Ana López",     "email": "ana@mail.com",    "password": "123456", "estilo": "textual"},
]

MATERIAS = [
    {"id": "mat-prog",    "nombre": "Introducción a la Programación",  "desc": "Variables, control de flujo, funciones y OOP básico.",                        "diff": 1.0, "horas": 60,  "frec": "trimestral"},
    {"id": "mat-prog-ii", "nombre": "Programación II",                 "desc": "POO avanzada, patrones de diseño, testing y buenas prácticas.",              "diff": 2.0, "horas": 80,  "frec": "trimestral"},
    {"id": "mat-estruc",  "nombre": "Estructuras de Datos",            "desc": "Listas, pilas, colas, árboles, grafos y análisis de complejidad.",            "diff": 2.0, "horas": 80,  "frec": "trimestral"},
    {"id": "mat-fund",    "nombre": "Fundamentos de Datos",            "desc": "Modelado, normalización, SQL básico y álgebra relacional.",                   "diff": 1.5, "horas": 60,  "frec": "trimestral"},
    {"id": "mat-fund-ii", "nombre": "Fundamentos de Datos II",         "desc": "Modelado avanzado, álgebra relacional aplicada y tuning de queries.",         "diff": 2.5, "horas": 70,  "frec": "trimestral"},
    {"id": "mat-bdrel",   "nombre": "Bases de Datos Relacionales",     "desc": "PostgreSQL, índices, transacciones, ACID, optimización de consultas.",       "diff": 2.5, "horas": 80,  "frec": "semestral"},
    {"id": "mat-bdrel-ii","nombre": "Bases de Datos Relacionales II",  "desc": "Replicación, particionamiento, PL/pgSQL y administración avanzada.",         "diff": 3.5, "horas": 90,  "frec": "semestral"},
    {"id": "mat-bdnosql", "nombre": "Bases de Datos NoSQL",            "desc": "MongoDB, Neo4j, Redis — modelado y casos de uso.",                           "diff": 3.0, "horas": 70,  "frec": "semestral"},
    {"id": "mat-mineria", "nombre": "Minería de Datos",                "desc": "Preprocesamiento, clustering, clasificación y reglas de asociación.",         "diff": 3.5, "horas": 90,  "frec": "semestral"},
    {"id": "mat-ml",      "nombre": "Machine Learning",                "desc": "Regresión, árboles de decisión, SVM, redes neuronales y ensambles.",         "diff": 4.0, "horas": 100, "frec": "semestral"},
    {"id": "mat-viz",     "nombre": "Visualización de Datos",          "desc": "Tableau, matplotlib, dashboards interactivos y storytelling.",               "diff": 1.5, "horas": 50,  "frec": "trimestral"},
    {"id": "mat-ingav",   "nombre": "Ingeniería de Datos Avanzada",    "desc": "Pipelines ETL, data lakes, Kafka, Airflow y arquitecturas cloud.",           "diff": 4.5, "horas": 120, "frec": "anual"},
]

# prereq → (origen, destino, peso, obligatorio, secuela)
PRERREQUISITOS = [
    # Secuelas directas (secuela=True)
    ("mat-prog-ii", "mat-prog",    1.0, True, True),
    ("mat-fund-ii", "mat-fund",    1.0, True, True),
    ("mat-bdrel-ii","mat-bdrel",   1.0, True, True),
    # Prerrequisitos normales (secuela=False)
    ("mat-estruc",  "mat-prog",    1.0, True, False),
    ("mat-bdrel",   "mat-fund",    1.0, True, False),
    ("mat-bdnosql", "mat-bdrel",   0.8, True, False),
    ("mat-mineria", "mat-bdrel",   0.6, True, False),
    ("mat-ml",      "mat-mineria", 0.9, True, False),
    ("mat-ml",      "mat-estruc",  0.7, True, False),
    ("mat-viz",     "mat-fund",    0.4, True, False),
    ("mat-ingav",   "mat-ml",      1.0, True, False),
    ("mat-ingav",   "mat-bdnosql", 0.8, True, False),
]

ALTERNATIVAS = [
    ("mat-bdnosql", "mat-bdrel", 0.5, "kinestésico"),
]

RECURSOS = [
    {"id": "rec-py01",    "nombre": "Python Básico — Apunte PDF",           "tipo": "pdf",   "mime": "application/pdf",    "archivo": "python_basico.pdf"},
    {"id": "rec-sql01",   "nombre": "SQL Fundamentals — Video",             "tipo": "video", "mime": "video/mp4",          "archivo": "sql_fundamentals.mp4", "link": "https://youtube.com/example"},
    {"id": "rec-bd01",    "nombre": "PostgreSQL Internals — Lectura",       "tipo": "pdf",   "mime": "application/pdf",    "archivo": "postgres_internals.pdf"},
    {"id": "rec-nosql01", "nombre": "MongoDB Aggregation Pipeline — Video", "tipo": "video", "mime": "video/mp4",          "archivo": "mongo_agg.mp4",       "link": "https://youtube.com/example2"},
    {"id": "rec-ml01",    "nombre": "Scikit-Learn Guide — Notebook",        "tipo": "pdf",   "mime": "application/pdf",    "archivo": "sklearn_guide.pdf"},
    {"id": "rec-viz01",   "nombre": "Dashboards con Tableau — Tutorial",    "tipo": "video", "mime": "video/mp4",          "archivo": "tableau_tutorial.mp4", "link": "https://youtube.com/example3"},
]

ACTIVIDADES = [
    {"id": "act-py01",    "nombre": "Ejercicios de Python — Quiz",           "tipo": "quiz",       "diff": 1.0, "puntaje": 100},
    {"id": "act-sql01",   "nombre": "Consultas SQL — Ejercicio práctico",    "tipo": "ejercicio",  "diff": 1.5, "puntaje": 80},
    {"id": "act-bd01",    "nombre": "Optimización de queries — Proyecto",    "tipo": "proyecto",   "diff": 2.5, "puntaje": 120},
    {"id": "act-nosql01", "nombre": "Modelado NoSQL — Caso de estudio",      "tipo": "ejercicio",  "diff": 2.0, "puntaje": 100},
    {"id": "act-ml01",    "nombre": "Modelo de clasificación — Proyecto",    "tipo": "proyecto",   "diff": 4.0, "puntaje": 150},
    {"id": "act-viz01",   "nombre": "Dashboard interactivo — Proyecto",      "tipo": "proyecto",   "diff": 2.0, "puntaje": 100},
]

PREGUNTAS = [
    {
        "uid": "preg-01",
        "texto": "¿Cuál es la capital de Francia?",
        "opciones": ["Londres", "París", "Madrid", "Berlín"],
        "respuesta_correcta": 1,
        "puntaje": 20,
    },
    {
        "uid": "preg-02",
        "texto": "¿Cuánto es 2 + 2?",
        "opciones": ["3", "22", "4", "5"],
        "respuesta_correcta": 2,
        "puntaje": 20,
    },
    {
        "uid": "preg-03",
        "texto": "¿Qué lenguaje se ejecuta en el navegador?",
        "opciones": ["Python", "Java", "C++", "JavaScript"],
        "respuesta_correcta": 3,
        "puntaje": 20,
    },
    {
        "uid": "preg-04",
        "texto": "¿Cuál es el planeta más cercano al Sol?",
        "opciones": ["Venus", "Mercurio", "Tierra", "Marte"],
        "respuesta_correcta": 1,
        "puntaje": 20,
    },
    {
        "uid": "preg-05",
        "texto": "¿Cuántos bits tiene un byte?",
        "opciones": ["4", "16", "8", "32"],
        "respuesta_correcta": 2,
        "puntaje": 20,
    },
]

# ═══════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════

def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _camino_estandar(nombre_materia: str) -> dict:
    """Genera un camino de aprendizaje genérico con los recursos y actividades."""
    return {
        "nombre": f"Camino estándar — {nombre_materia}",
        "descripcion": None,
        "secuencia": [
            {"tipo": "recurso",   "id": "rec-py01"},
            {"tipo": "actividad", "id": "act-py01"},
            {"tipo": "recurso",   "id": "rec-sql01"},
            {"tipo": "actividad", "id": "act-sql01"},
            {"tipo": "recurso",   "id": "rec-viz01"},
            {"tipo": "actividad", "id": "act-viz01"},
        ],
    }

# ═══════════════════════════════════════════════════════════
# Seed functions
# ═══════════════════════════════════════════════════════════

def _crear_indices(db) -> None:
    """Crea los índices de MongoDB declarados en Etapa 1."""
    db.intentos.create_index([("estudiante.uid", 1), ("inicio", -1)])
    db.sesiones.create_index([("estudiante.uid", 1), ("fecha_ini", -1)])
    db.eventos_interaccion.create_index([("id_usuario", 1), ("timestamp", -1)])
    db.eventos_interaccion.create_index([("tema", 1), ("tipo_evento", 1)])
    db.curriculum.create_index([("id_materia", 1)], unique=True)
    print("[Mongo] Índices creados ✓")


def seed_mongo(mongo: MongoService) -> None:
    db = mongo.db
    print("[Mongo] Limpiando colecciones...")
    db.estudiantes.delete_many({})
    db.curriculum.delete_many({})
    db.recursos.delete_many({})
    db.actividades.delete_many({})
    db.sesiones.delete_many({})
    db.intentos.delete_many({})
    db.eventos_interaccion.delete_many({})

    print("[Mongo] Insertando estudiantes...")
    for e in ESTUDIANTES:
        db.estudiantes.insert_one({
            "uid": e["id"],
            "nombre": e["nombre"],
            "email": e["email"],
            "password_hash": _hash(e["password"]),
            "estilo_preferido": e["estilo"],
        })

    print("[Mongo] Insertando recursos...")
    pdf_path = Path(__file__).resolve().parent / "seed_files" / "pdf" / "867-Article Text-2420-1-10-20240722.pdf"
    pdf_bin = bson.Binary(pdf_path.read_bytes())

    for r in RECURSOS:
        doc = {
            "uid": r["id"],
            "nombre": r["nombre"],
            "tipo": r["tipo"],
            "mime_type": r["mime"],
            "nombre_archivo": r["archivo"],
            "recurso_bin": pdf_bin,
            "link_aux": r.get("link"),
        }
        db.recursos.insert_one(doc)

    print("[Mongo] Insertando actividades...")
    for a in ACTIVIDADES:
        db.actividades.insert_one({
            "uid": a["id"],
            "nombre": a["nombre"],
            "tipo": a["tipo"],
            "dificultad": a["diff"],
            "puntaje_maximo": a["puntaje"],
            "preguntas": PREGUNTAS,
        })

    print("[Mongo] Insertando currículums...")
    for m in MATERIAS:
        camino = _camino_estandar(m["nombre"])
        db.curriculum.insert_one({
            "uid": m["id"],
            "id_materia": m["id"],
            "nombre": m["nombre"],
            "tiempo_estimado_horas": m["horas"],
            "caminos": {
                "visual":      camino,
                "auditivo":    camino,
                "kinestesico": camino,
                "escrito":     camino,
            },
        })

    _crear_indices(db)
    _seed_sesiones_e_intentos(db)
    _seed_eventos_interaccion(db)
    print("[Mongo] Seed completo ✓")


def _seed_sesiones_e_intentos(db) -> None:
    """Genera sesiones e intentos simulados para que analytics devuelva datos reales."""
    from datetime import timedelta

    ahora = datetime.now(timezone.utc)

    # Mapa id → datos completos del estudiante (necesarios para que Sesion(**doc) no falle)
    est_map = {e["id"]: e for e in ESTUDIANTES}

    sesiones_data = [
        {"uid": "ses-001", "est": "est-001", "delta_h": 24,  "dur_m": 45, "fatiga": 0.3},
        {"uid": "ses-002", "est": "est-001", "delta_h": 48,  "dur_m": 30, "fatiga": 0.5},
        {"uid": "ses-003", "est": "est-001", "delta_h": 72,  "dur_m": 60, "fatiga": 0.7},
        {"uid": "ses-004", "est": "est-002", "delta_h": 12,  "dur_m": 50, "fatiga": 0.2},
        {"uid": "ses-005", "est": "est-002", "delta_h": 36,  "dur_m": 40, "fatiga": 0.4},
        {"uid": "ses-006", "est": "est-003", "delta_h": 6,   "dur_m": 25, "fatiga": 0.6},
        {"uid": "ses-007", "est": "est-004", "delta_h": 20,  "dur_m": 35, "fatiga": 0.3},
    ]

    for s in sesiones_data:
        e = est_map[s["est"]]
        fecha_ini = ahora - timedelta(hours=s["delta_h"])
        fecha_fin = fecha_ini + timedelta(minutes=s["dur_m"])
        db.sesiones.insert_one({
            "uid": s["uid"],
            "estudiante": {
                "uid": e["id"],
                "nombre": e["nombre"],
                "email": e["email"],
                "estilo_preferido": e["estilo"],
                "password_hash": "",   # no se usa en analytics
            },
            "fecha_ini": fecha_ini,
            "fecha_fin": fecha_fin,
            "intentos_estudio": [],
            "fatiga_estimada": s["fatiga"],
        })

    intentos_data = [
        # est-001 tiene 4 intentos malos en mat-prog (activa el warning)
        {"uid": "int-001", "est": "est-001", "nom": "Juan Pérez", "ses": "ses-001",
         "mat": "mat-prog", "cont": "act-py01", "tipo": "actividad",
         "aprobado": False, "terminado": True,  "dur": 300, "aciertos": 2, "errores": 8},
        {"uid": "int-002", "est": "est-001", "nom": "Juan Pérez", "ses": "ses-002",
         "mat": "mat-prog", "cont": "act-py01", "tipo": "actividad",
         "aprobado": False, "terminado": True,  "dur": 280, "aciertos": 3, "errores": 7},
        {"uid": "int-003", "est": "est-001", "nom": "Juan Pérez", "ses": "ses-002",
         "mat": "mat-prog", "cont": "act-py01", "tipo": "actividad",
         "aprobado": False, "terminado": False, "dur": 120, "aciertos": 0, "errores": 0},
        {"uid": "int-004", "est": "est-001", "nom": "Juan Pérez", "ses": "ses-003",
         "mat": "mat-prog", "cont": "act-py01", "tipo": "actividad",
         "aprobado": False, "terminado": True,  "dur": 310, "aciertos": 1, "errores": 9},
        # est-002 tiene buenos resultados
        {"uid": "int-005", "est": "est-002", "nom": "María Gómez", "ses": "ses-004",
         "mat": "mat-bdrel", "cont": "act-bd01", "tipo": "actividad",
         "aprobado": True,  "terminado": True,  "dur": 600, "aciertos": 9, "errores": 1},
        {"uid": "int-006", "est": "est-002", "nom": "María Gómez", "ses": "ses-005",
         "mat": "mat-bdrel", "cont": "act-sql01", "tipo": "actividad",
         "aprobado": True,  "terminado": True,  "dur": 450, "aciertos": 8, "errores": 2},
        # est-003
        {"uid": "int-007", "est": "est-003", "nom": "Pedro Ruiz", "ses": "ses-006",
         "mat": "mat-viz",  "cont": "act-viz01", "tipo": "actividad",
         "aprobado": False, "terminado": False, "dur": 100, "aciertos": 0, "errores": 0},
        # est-004
        {"uid": "int-008", "est": "est-004", "nom": "Ana López", "ses": "ses-007",
         "mat": "mat-ml",   "cont": "act-ml01", "tipo": "actividad",
         "aprobado": True,  "terminado": True,  "dur": 900, "aciertos": 10, "errores": 0},
    ]

    ahora = datetime.now(timezone.utc)
    for i in intentos_data:
        e = est_map[i["est"]]
        db.intentos.insert_one({
            "uid": i["uid"],
            "estudiante": {
                "uid": e["id"],
                "nombre": e["nombre"],
                "email": e["email"],
                "estilo_preferido": e["estilo"],
                "password_hash": "",
            },
            "id_sesion": i["ses"],
            "id_materia": i["mat"],
            "id_contenido": i["cont"],
            "tipo_contenido": i["tipo"],
            "inicio": ahora - timedelta(minutes=i["dur"] + 10),
            "fin": ahora - timedelta(minutes=10),
            "duracion_segundos": i["dur"],
            "pausas": 0,
            "duracion_pausa_segundos": 0,
            "terminado": i["terminado"],
            "aprobado": i["aprobado"],
            "aciertos": i["aciertos"],
            "errores": i["errores"],
            "puntaje": i["aciertos"] * 10.0,
        })

    print("[Mongo] Sesiones e intentos simulados ✓")


def _seed_eventos_interaccion(db) -> None:
    """Genera ~20 EventoInteraccion para demostrar Consultas 3 y 4."""
    from datetime import timedelta

    ahora = datetime.now(timezone.utc)

    eventos = [
        # est-001 — múltiples fallos en mat-prog
        ("ev-01", "est-001", "Juan Pérez",  "ses-001", "inicio_intento",    "mat-prog",    "act-py01",  20),
        ("ev-02", "est-001", "Juan Pérez",  "ses-001", "cierre_intento",    "mat-prog",    "act-py01",  19),
        ("ev-03", "est-001", "Juan Pérez",  "ses-002", "inicio_intento",    "mat-prog",    "act-py01",  18),
        ("ev-04", "est-001", "Juan Pérez",  "ses-002", "abandono_actividad","mat-prog",    "act-py01",  17),
        ("ev-05", "est-001", "Juan Pérez",  "ses-002", "inicio_intento",    "mat-prog",    "act-py01",  16),
        ("ev-06", "est-001", "Juan Pérez",  "ses-002", "cierre_intento",    "mat-prog",    "act-py01",  15),
        ("ev-07", "est-001", "Juan Pérez",  "ses-003", "inicio_intento",    "mat-prog",    "act-py01",  14),
        ("ev-08", "est-001", "Juan Pérez",  "ses-003", "cierre_intento",    "mat-prog",    "act-py01",  13),
        # est-001 — también accede a recursos
        ("ev-09", "est-001", "Juan Pérez",  "ses-001", "acceso_recurso",    "mat-prog",    "rec-py01",  22),
        # est-002 — aprendizaje fluido
        ("ev-10", "est-002", "María Gómez", "ses-004", "inicio_intento",    "mat-bdrel",   "act-bd01",  10),
        ("ev-11", "est-002", "María Gómez", "ses-004", "cierre_intento",    "mat-bdrel",   "act-bd01",   9),
        ("ev-12", "est-002", "María Gómez", "ses-004", "acceso_recurso",    "mat-bdrel",   "rec-bd01",  11),
        ("ev-13", "est-002", "María Gómez", "ses-005", "inicio_intento",    "mat-bdrel",   "act-sql01",  5),
        ("ev-14", "est-002", "María Gómez", "ses-005", "cierre_intento",    "mat-bdrel",   "act-sql01",  4),
        # est-003 — abandono
        ("ev-15", "est-003", "Pedro Ruiz",  "ses-006", "inicio_intento",    "mat-viz",     "act-viz01",  3),
        ("ev-16", "est-003", "Pedro Ruiz",  "ses-006", "abandono_actividad","mat-viz",     "act-viz01",  2),
        # est-004 — aprendizaje exitoso
        ("ev-17", "est-004", "Ana López",   "ses-007", "acceso_recurso",    "mat-ml",      "rec-ml01",  12),
        ("ev-18", "est-004", "Ana López",   "ses-007", "inicio_intento",    "mat-ml",      "act-ml01",   8),
        ("ev-19", "est-004", "Ana López",   "ses-007", "cierre_intento",    "mat-ml",      "act-ml01",   7),
        ("ev-20", "est-001", "Juan Pérez",  "ses-001", "acceso_recurso",    "mat-fund",    "rec-sql01",  30),
    ]

    for uid, id_est, nombre, id_ses, tipo, mat, cont, min_ago in eventos:
        db.eventos_interaccion.insert_one({
            "uid": uid,
            "id_usuario": id_est,
            "nombre_usuario": nombre,
            "id_sesion": id_ses,
            "tipo_evento": tipo,
            "timestamp": ahora - timedelta(minutes=min_ago),
            "id_materia": mat,
            "id_contenido": cont,
            "tema": mat,
        })

    print("[Mongo] EventoInteraccion simulados ✓")


def seed_neo4j(neo4j: Neo4jService) -> None:
    print("[Neo4j] Limpiando grafo...")
    neo4j.write("MATCH (n) DETACH DELETE n")

    print("[Neo4j] Insertando estudiantes...")
    for e in ESTUDIANTES:
        neo4j.write("""
            CREATE (:Estudiante {
                id: $id,
                nombre: $nombre,
                estilo_preferido: $estilo
            })
        """, id=e["id"], nombre=e["nombre"], estilo=e["estilo"])

    print("[Neo4j] Insertando materias...")
    for m in MATERIAS:
        neo4j.write("""
            CREATE (:Materia {
                id: $id,
                nombre: $nombre,
                descripcion: $desc,
                nivel_dificultad: $diff,
                tiempo_estimado: $horas,
                frecuencia_uso: $frec
            })
        """, id=m["id"], nombre=m["nombre"], desc=m["desc"],
             diff=m["diff"], horas=m["horas"], frec=m["frec"])

    print("[Neo4j] Insertando recursos...")
    for r in RECURSOS:
        neo4j.write("""
            CREATE (:Recurso {
                id: $id,
                tipo: $tipo,
                duracion_estimada: 30,
                carga_cognitiva: 0.5,
                estilo_aprendizaje_opt: 'visual'
            })
        """, id=r["id"], tipo=r["tipo"])

    print("[Neo4j] Insertando actividades...")
    for a in ACTIVIDADES:
        neo4j.write("""
            CREATE (:Actividad {
                id: $id,
                nombre: $nombre,
                descripcion: $nombre,
                tipo: $tipo,
                dificultad: $diff,
                duracion_estimada: 45,
                puntaje_maximo: $puntaje
            })
        """, id=a["id"], nombre=a["nombre"], tipo=a["tipo"],
             diff=a["diff"], puntaje=a["puntaje"])

    print("[Neo4j] Creando prerrequisitos...")
    for origen, destino, peso, oblig, secuela in PRERREQUISITOS:
        neo4j.write("""
            MATCH (a:Materia {id: $origen}), (b:Materia {id: $destino})
            MERGE (a)-[:REQUIERE {peso: $peso, obligatorio: $oblig, secuela: $secuela}]->(b)
        """, origen=origen, destino=destino, peso=peso, oblig=oblig, secuela=secuela)

    print("[Neo4j] Creando alternativas...")
    for origen, destino, peso, estilo in ALTERNATIVAS:
        neo4j.write("""
            MATCH (a:Materia {id: $origen}), (b:Materia {id: $destino})
            MERGE (a)-[:ALTERNATIVA {peso_adicional: $peso, estilo_favorecido: $estilo}]->(b)
        """, origen=origen, destino=destino, peso=peso, estilo=estilo)

    print("[Neo4j] Anotando estudiantes en materias...")
    enrollments = [
        ("est-001", "mat-prog"),    ("est-001", "mat-fund"),
        ("est-001", "mat-prog-ii"),
        ("est-002", "mat-prog"),    ("est-002", "mat-fund"),
        ("est-002", "mat-bdrel"),   ("est-002", "mat-fund-ii"),
        ("est-003", "mat-prog"),    ("est-003", "mat-viz"),
        ("est-003", "mat-prog-ii"),
        ("est-004", "mat-fund"),    ("est-004", "mat-bdrel"),
        ("est-004", "mat-ml"),      ("est-004", "mat-bdrel-ii"),
    ]
    for est_id, mat_id in enrollments:
        neo4j.write("""
            MATCH (e:Estudiante {id: $est_id}), (m:Materia {id: $mat_id})
            CREATE (e)-[:ANOTADO_EN {
                completado: false,
                fecha_inicio: $ahora,
                fecha_fin: null,
                estilo_actual: 'visual'
            }]->(m)
        """, est_id=est_id, mat_id=mat_id,
             ahora=datetime.now(timezone.utc).isoformat())

    print("[Neo4j] Creando amistades...")
    friendships = [("est-001", "est-002"), ("est-002", "est-003"), ("est-003", "est-004")]
    for a_id, b_id in friendships:
        neo4j.write("""
            MATCH (a:Estudiante {id: $a}), (b:Estudiante {id: $b})
            MERGE (a)-[:COMPAÑERO_DE {solicitud_aceptada: true, fecha_desde: $hoy}]-(b)
        """, a=a_id, b=b_id, hoy=datetime.now(timezone.utc).isoformat())

    print("[Neo4j] Creando relaciones de estudio compartido...")
    neo4j.write("""
        MATCH (a:Estudiante {id: 'est-001'}), (b:Estudiante {id: 'est-002'})
        MERGE (a)-[:ESTUDIO_CON {id_recurso: 'rec-py01', id_intento: 'int-dummy', exito: true}]-(b)
    """)
    neo4j.write("""
        MATCH (a:Estudiante {id: 'est-002'}), (b:Estudiante {id: 'est-003'})
        MERGE (a)-[:ESTUDIO_CON {id_recurso: 'rec-sql01', id_intento: 'int-dummy', exito: false}]-(b)
    """)

    print("[Neo4j] Seed completo ✓")


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════

def main():
    mongo = MongoService(settings.mongo_uri)
    neo4j = Neo4jService(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)

    with mongo, neo4j:
        seed_mongo(mongo)
        seed_neo4j(neo4j)

    print("✓ Bases de datos pobladas correctamente.")


if __name__ == "__main__":
    main()
