"""Seed script — populates MongoDB and Neo4j with sample data."""

import uuid
from datetime import datetime, timezone

import bcrypt

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
    {"id": "mat-estruc",  "nombre": "Estructuras de Datos",            "desc": "Listas, pilas, colas, árboles, grafos y análisis de complejidad.",            "diff": 2.0, "horas": 80,  "frec": "trimestral"},
    {"id": "mat-fund",    "nombre": "Fundamentos de Datos",            "desc": "Modelado, normalización, SQL básico y álgebra relacional.",                   "diff": 1.5, "horas": 60,  "frec": "trimestral"},
    {"id": "mat-bdrel",   "nombre": "Bases de Datos Relacionales",     "desc": "PostgreSQL, índices, transacciones, ACID, optimización de consultas.",       "diff": 2.5, "horas": 80,  "frec": "semestral"},
    {"id": "mat-bdnosql", "nombre": "Bases de Datos NoSQL",            "desc": "MongoDB, Neo4j, Redis — modelado y casos de uso.",                           "diff": 3.0, "horas": 70,  "frec": "semestral"},
    {"id": "mat-mineria", "nombre": "Minería de Datos",                "desc": "Preprocesamiento, clustering, clasificación y reglas de asociación.",         "diff": 3.5, "horas": 90,  "frec": "semestral"},
    {"id": "mat-ml",      "nombre": "Machine Learning",                "desc": "Regresión, árboles de decisión, SVM, redes neuronales y ensambles.",         "diff": 4.0, "horas": 100, "frec": "semestral"},
    {"id": "mat-viz",     "nombre": "Visualización de Datos",          "desc": "Tableau, matplotlib, dashboards interactivos y storytelling.",               "diff": 1.5, "horas": 50,  "frec": "trimestral"},
    {"id": "mat-ingav",   "nombre": "Ingeniería de Datos Avanzada",    "desc": "Pipelines ETL, data lakes, Kafka, Airflow y arquitecturas cloud.",           "diff": 4.5, "horas": 120, "frec": "anual"},
]

# prereq → {requiere: id, peso, obligatorio}
PRERREQUISITOS = [
    ("mat-estruc",  "mat-prog",    1.0, True),
    ("mat-bdrel",   "mat-fund",    1.0, True),
    ("mat-bdnosql", "mat-bdrel",   0.8, True),
    ("mat-mineria", "mat-bdrel",   0.6, True),
    ("mat-ml",      "mat-mineria", 0.9, True),
    ("mat-ml",      "mat-estruc",  0.7, True),
    ("mat-viz",     "mat-fund",    0.4, True),
    ("mat-ingav",   "mat-ml",      1.0, True),
    ("mat-ingav",   "mat-bdnosql", 0.8, True),
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

def seed_mongo(mongo: MongoService) -> None:
    db = mongo.db
    print("[Mongo] Limpiando colecciones...")
    db.estudiantes.delete_many({})
    db.curriculum.delete_many({})
    db.recursos.delete_many({})
    db.actividades.delete_many({})

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
    for r in RECURSOS:
        db.recursos.insert_one({
            "uid": r["id"],
            "nombre": r["nombre"],
            "tipo": r["tipo"],
            "mime_type": r["mime"],
            "nombre_archivo": r["archivo"],
            "link_aux": r.get("link"),
        })

    print("[Mongo] Insertando actividades...")
    for a in ACTIVIDADES:
        db.actividades.insert_one({
            "uid": a["id"],
            "nombre": a["nombre"],
            "tipo": a["tipo"],
            "dificultad": a["diff"],
            "puntaje_maximo": a["puntaje"],
            "preguntas": [],
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

    print("[Mongo] Seed completo ✓")


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
    for origen, destino, peso, oblig in PRERREQUISITOS:
        neo4j.write("""
            MATCH (a:Materia {id: $origen}), (b:Materia {id: $destino})
            MERGE (a)-[:REQUIERE {peso: $peso, obligatorio: $oblig}]->(b)
        """, origen=origen, destino=destino, peso=peso, oblig=oblig)

    print("[Neo4j] Creando alternativas...")
    for origen, destino, peso, estilo in ALTERNATIVAS:
        neo4j.write("""
            MATCH (a:Materia {id: $origen}), (b:Materia {id: $destino})
            MERGE (a)-[:ALTERNATIVA {peso_adicional: $peso, estilo_favorecido: $estilo}]->(b)
        """, origen=origen, destino=destino, peso=peso, estilo=estilo)

    print("[Neo4j] Anotando estudiantes en materias...")
    enrollments = [
        ("est-001", "mat-prog"),    ("est-001", "mat-fund"),
        ("est-002", "mat-prog"),    ("est-002", "mat-fund"),
        ("est-002", "mat-bdrel"),
        ("est-003", "mat-prog"),    ("est-003", "mat-viz"),
        ("est-004", "mat-fund"),    ("est-004", "mat-bdrel"),
        ("est-004", "mat-ml"),
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
