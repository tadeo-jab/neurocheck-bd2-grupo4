"""Populate MongoDB and Neo4j with mock data for local development."""

import sys
from pathlib import Path

# Asegura que src/ sea importable desde cualquier directorio
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta
import random

from src.config import settings
from src.db.mongo import MongoService
from src.db.neo4j import Neo4jService

# --- Node models ---
from src.models.node_models import Student as NeoStudent
from src.models.node_models import Concept, Activity, Resource, Subject

# --- Relationship models ---
from src.models.relationship_models import (
    Studies, Completes, Requires, BelongsTo, Deepens,
    Evaluates, Explains, CorrelatesWith, AlternativeTo,
)

# --- MongoDB collection models ---
from src.models.collection_models import (
    Student as MongoStudent,
    StudentPreferences,
    StudentMetrics,
    StudentProgress,
    StudySession,
    InteractionEvent,
)

random.seed(42)

# ── Neo4j data ────────────────────────────────────────────────────────

SUBJECTS = [
    Subject(uid="s-neurologia-clinica", name="Neurología Clínica", difficulty_level=4.0),
    Subject(uid="s-neuroanatomia", name="Neuroanatomía", difficulty_level=3.5),
    Subject(uid="s-neurofisiologia", name="Neurofisiología", difficulty_level=4.5),
    Subject(uid="s-neurofarmacologia", name="Neurofarmacología", difficulty_level=4.0),
    Subject(uid="s-neuropsicologia", name="Neuropsicología", difficulty_level=3.0),
]

CONCEPTS = [
    # Neurología Clínica
    Concept(uid="c-eval-neuro", name="Evaluación Neurológica", description="Historia clínica y examen físico neurológico", difficulty_level=3.0, estimated_time_minutes=120, usage_frequency=95),
    Concept(uid="c-trastornos-mov", name="Trastornos del Movimiento", description="Parkinson, temblor esencial, distonías", difficulty_level=4.0, estimated_time_minutes=180, usage_frequency=70),
    Concept(uid="c-epilepsia", name="Epilepsia y Crisis", description="Clasificación, diagnóstico y tratamiento de crisis epilépticas", difficulty_level=4.5, estimated_time_minutes=150, usage_frequency=60),
    Concept(uid="c-cefaleas", name="Cefaleas", description="Migraña, cefalea tensional, cefalea en racimos", difficulty_level=2.5, estimated_time_minutes=90, usage_frequency=80),
    # Neuroanatomía
    Concept(uid="c-corteza", name="Corteza Cerebral", description="Áreas de Brodmann, organización laminar y columnar", difficulty_level=3.5, estimated_time_minutes=120, usage_frequency=85),
    Concept(uid="c-sistema-limbico", name="Sistema Límbico", description="Amígdala, hipocampo, giro cingulado y sus conexiones", difficulty_level=4.0, estimated_time_minutes=100, usage_frequency=65),
    Concept(uid="c-vias-motoras", name="Vías Motoras", description="Tracto corticoespinal, extrapiramidal y cerebelo", difficulty_level=4.5, estimated_time_minutes=150, usage_frequency=55),
    Concept(uid="c-ganglios-basales", name="Ganglios Basales", description="Circuitos de los ganglios basales y su rol en el movimiento", difficulty_level=4.0, estimated_time_minutes=120, usage_frequency=50),
    # Neurofisiología
    Concept(uid="c-potencial-accion", name="Potencial de Acción", description="Canales iónicos, despolarización, repolarización e hiperpolarización", difficulty_level=3.0, estimated_time_minutes=90, usage_frequency=90),
    Concept(uid="c-sinapsis", name="Transmisión Sináptica", description="Sinapsis químicas y eléctricas, neurotransmisores", difficulty_level=3.5, estimated_time_minutes=100, usage_frequency=85),
    Concept(uid="c-plasticidad", name="Plasticidad Neuronal", description="LTP, LTD, neurogénesis y reorganización sináptica", difficulty_level=5.0, estimated_time_minutes=120, usage_frequency=40),
    # Neurofarmacología
    Concept(uid="c-neurotransmisores", name="Sistemas de Neurotransmisores", description="Dopamina, serotonina, noradrenalina, GABA, glutamato", difficulty_level=3.5, estimated_time_minutes=120, usage_frequency=75),
    Concept(uid="c-psicofarmacos", name="Psicofármacos", description="Antidepresivos, ansiolíticos, antipsicóticos, estabilizadores", difficulty_level=4.0, estimated_time_minutes=150, usage_frequency=65),
    # Neuropsicología
    Concept(uid="c-funciones-ejecutivas", name="Funciones Ejecutivas", description="Planificación, inhibición, memoria de trabajo, flexibilidad cognitiva", difficulty_level=3.0, estimated_time_minutes=100, usage_frequency=80),
    Concept(uid="c-memoria", name="Memoria y Aprendizaje", description="Tipos de memoria, consolidación y recuperación", difficulty_level=2.5, estimated_time_minutes=90, usage_frequency=90),
]

# Concept → Subject mapping (BELONGS_TO)
CONCEPT_SUBJECT_MAP = {
    "c-eval-neuro": ("s-neurologia-clinica", 1.0),
    "c-trastornos-mov": ("s-neurologia-clinica", 1.0),
    "c-epilepsia": ("s-neurologia-clinica", 1.0),
    "c-cefaleas": ("s-neurologia-clinica", 0.8),
    "c-corteza": ("s-neuroanatomia", 1.0),
    "c-sistema-limbico": ("s-neuroanatomia", 1.0),
    "c-vias-motoras": ("s-neuroanatomia", 1.0),
    "c-ganglios-basales": ("s-neuroanatomia", 1.0),
    "c-potencial-accion": ("s-neurofisiologia", 1.0),
    "c-sinapsis": ("s-neurofisiologia", 1.0),
    "c-plasticidad": ("s-neurofisiologia", 1.0),
    "c-neurotransmisores": ("s-neurofarmacologia", 1.0),
    "c-psicofarmacos": ("s-neurofarmacologia", 1.0),
    "c-funciones-ejecutivas": ("s-neuropsicologia", 1.0),
    "c-memoria": ("s-neuropsicologia", 1.0),
}

# Concept prereqs (REQUIRES): advanced → prerequisite
CONCEPT_REQUIRES = [
    ("c-epilepsia", "c-potencial-accion", 0.9, "intermedio", "Requiere entender despolarización neuronal"),
    ("c-epilepsia", "c-sinapsis", 0.7, "intermedio", "Mecanismos sinápticos en epileptogénesis"),
    ("c-trastornos-mov", "c-ganglios-basales", 1.0, "avanzado", "Los ganglios basales son la base anatómica"),
    ("c-trastornos-mov", "c-vias-motoras", 0.8, "avanzado", ""),
    ("c-psicofarmacos", "c-neurotransmisores", 1.0, "intermedio", "Base neuroquímica de los psicofármacos"),
    ("c-plasticidad", "c-sinapsis", 0.9, "avanzado", "LTP y LTD ocurren en las sinapsis"),
    ("c-plasticidad", "c-potencial-accion", 0.5, "intermedio", ""),
    ("c-sistema-limbico", "c-corteza", 0.6, "básico", ""),
    ("c-funciones-ejecutivas", "c-corteza", 0.7, "intermedio", "La corteza prefrontal sustenta las funciones ejecutivas"),
    ("c-funciones-ejecutivas", "c-memoria", 0.5, "básico", ""),
]

# Concept correlations (CORRELATES_WITH)
CONCEPT_CORRELATIONS = [
    ("c-eval-neuro", "c-corteza", 0.7),
    ("c-eval-neuro", "c-vias-motoras", 0.6),
    ("c-trastornos-mov", "c-ganglios-basales", 0.9),
    ("c-epilepsia", "c-sinapsis", 0.8),
    ("c-cefaleas", "c-sistema-limbico", 0.4),
    ("c-memoria", "c-plasticidad", 0.9),
    ("c-memoria", "c-sistema-limbico", 0.8),
    ("c-psicofarmacos", "c-sinapsis", 0.7),
]

# Concept deepening (DEEPENS)
CONCEPT_DEEPENS = [
    ("c-plasticidad", "c-memoria", 0.8),
    ("c-epilepsia", "c-sinapsis", 0.7),
    ("c-trastornos-mov", "c-ganglios-basales", 0.9),
]

# Concept alternatives (ALTERNATIVE_TO)
CONCEPT_ALTERNATIVES = [
    ("c-potencial-accion", "c-sinapsis", 0.0, "visual"),
]

ACTIVITIES = [
    Activity(uid="a-quiz-eval-neuro", name="Quiz: Evaluación Neurológica", description="20 preguntas sobre examen neurológico", type="quiz",
             difficulty=3.0, estimated_time_minutes=30, cognitive_load=0.5, max_score=100),
    Activity(uid="a-simulacion-epilepsia", name="Simulación: Caso de Epilepsia", description="Caso clínico interactivo de crisis epiléptica", type="simulacion",
             difficulty=4.5, estimated_time_minutes=45, cognitive_load=0.8, max_score=100),
    Activity(uid="a-practico-parkinson", name="Ejercicio: Diagnóstico de Parkinson", description="Ejercicio con videos de pacientes", type="ejercicio",
             difficulty=4.0, estimated_time_minutes=40, cognitive_load=0.7, max_score=100),
    Activity(uid="a-quiz-anatomia", name="Quiz: Neuroanatomía Básica", description="Identificación de estructuras en cortes cerebrales", type="quiz",
             difficulty=3.5, estimated_time_minutes=25, cognitive_load=0.6, max_score=100),
    Activity(uid="a-quiz-neurotransmisores", name="Quiz: Neurotransmisores", description="Preguntas sobre sistemas de neurotransmisión", type="quiz",
             difficulty=3.0, estimated_time_minutes=20, cognitive_load=0.4, max_score=100),
    Activity(uid="a-lectura-plasticidad", name="Lectura: Plasticidad Neuronal", description="Artículo guiado con preguntas de comprensión", type="lectura",
             difficulty=5.0, estimated_time_minutes=60, cognitive_load=0.9, max_score=100),
    Activity(uid="a-ejercicio-memoria", name="Ejercicio: Evaluación de Memoria", description="Casos de evaluación neuropsicológica de memoria", type="ejercicio",
             difficulty=2.5, estimated_time_minutes=35, cognitive_load=0.5, max_score=100),
    Activity(uid="a-quiz-funciones-ejecutivas", name="Quiz: Funciones Ejecutivas", description="Test de conocimiento sobre funciones ejecutivas", type="quiz",
             difficulty=3.0, estimated_time_minutes=25, cognitive_load=0.5, max_score=100),
]

# Activity → Subject mapping (EVALUATES)
ACTIVITY_SUBJECT_MAP = [
    ("a-quiz-eval-neuro", "s-neurologia-clinica", 0.8, 0.7),
    ("a-simulacion-epilepsia", "s-neurologia-clinica", 0.9, 0.7),
    ("a-practico-parkinson", "s-neurologia-clinica", 0.7, 0.7),
    ("a-quiz-anatomia", "s-neuroanatomia", 0.8, 0.6),
    ("a-quiz-neurotransmisores", "s-neurofarmacologia", 0.9, 0.7),
    ("a-lectura-plasticidad", "s-neurofisiologia", 0.9, 0.7),
    ("a-ejercicio-memoria", "s-neuropsicologia", 0.8, 0.6),
    ("a-quiz-funciones-ejecutivas", "s-neuropsicologia", 0.8, 0.6),
]

RESOURCES = [
    Resource(uid="r-video-eval-neuro", type="video", duration=25, cognitive_load=0.4,
             url="https://example.com/videos/eval-neuro", optimal_learning_style=["visual", "auditivo"]),
    Resource(uid="r-articulo-parkinson", type="articulo", duration=40, cognitive_load=0.7,
             url="https://example.com/articulos/parkinson", optimal_learning_style=["lectura", "visual"]),
    Resource(uid="r-guia-sinapsis", type="guia", duration=30, cognitive_load=0.5,
             url="https://example.com/guias/sinapsis", optimal_learning_style=["visual", "kinestésico"]),
    Resource(uid="r-video-ganglios", type="video", duration=20, cognitive_load=0.5,
             url="https://example.com/videos/ganglios-basales", optimal_learning_style=["visual", "auditivo"]),
    Resource(uid="r-infografia-corteza", type="infografia", duration=10, cognitive_load=0.2,
             url="https://example.com/infografias/corteza", optimal_learning_style=["visual"]),
    Resource(uid="r-podcast-memoria", type="podcast", duration=35, cognitive_load=0.3,
             url="https://example.com/podcasts/memoria", optimal_learning_style=["auditivo"]),
    Resource(uid="r-articulo-plasticidad", type="articulo", duration=50, cognitive_load=0.9,
             url="https://example.com/articulos/plasticidad", optimal_learning_style=["lectura"]),
    Resource(uid="r-video-neurotransmisores", type="video", duration=15, cognitive_load=0.3,
             url="https://example.com/videos/neurotransmisores", optimal_learning_style=["visual", "auditivo"]),
]

# Resource → Concept mapping (EXPLAINS)
RESOURCE_CONCEPT_MAP = [
    ("r-video-eval-neuro", "c-eval-neuro", 0.9),
    ("r-articulo-parkinson", "c-trastornos-mov", 0.8),
    ("r-guia-sinapsis", "c-sinapsis", 0.9),
    ("r-video-ganglios", "c-ganglios-basales", 0.8),
    ("r-infografia-corteza", "c-corteza", 0.7),
    ("r-podcast-memoria", "c-memoria", 0.6),
    ("r-articulo-plasticidad", "c-plasticidad", 1.0),
    ("r-video-neurotransmisores", "c-neurotransmisores", 0.9),
    ("r-guia-sinapsis", "c-potencial-accion", 0.5),
    ("r-video-neurotransmisores", "c-psicofarmacos", 0.6),
]

NEO_STUDENTS = [
    NeoStudent(uid="st-laura-gomez", name="Laura Gómez", mastery_level=0.75, preferred_style="visual"),
    NeoStudent(uid="st-carlos-ruiz", name="Carlos Ruiz", mastery_level=0.45, preferred_style="lectura"),
    NeoStudent(uid="st-ana-martinez", name="Ana Martínez", mastery_level=0.90, preferred_style="kinestésico"),
    NeoStudent(uid="st-diego-vega", name="Diego Vega", mastery_level=0.30, preferred_style="auditivo"),
    NeoStudent(uid="st-elena-castro", name="Elena Castro", mastery_level=0.60, preferred_style="visual"),
]

# STUDIES relationships (Student → Concept)
def _make_studies():
    studies = []
    for st in NEO_STUDENTS:
        for c in random.sample(CONCEPTS, k=random.randint(4, 8)):
            total_min = random.randint(30, 300)
            times = random.randint(1, 8)
            ml = round(random.uniform(0.2, 1.0), 2)
            studies.append((st.uid, c.uid, Studies(
                total_time_minutes=total_min, times_studied=times, mastery_level=ml,
            )))
    return studies

STUDIES_DATA = _make_studies()

# COMPLETES relationships (Student → Activity)
def _make_completes():
    completes = []
    for st in NEO_STUDENTS:
        for a in random.sample(ACTIVITIES, k=random.randint(2, 5)):
            score = round(random.uniform(40, 100), 1)
            tts = random.randint(600, 3600)
            attempts = random.randint(1, 4)
            approved = score >= 70
            completes.append((st.uid, a.uid, Completes(
                score_obtained=score, time_taken_seconds=tts, attempts=attempts, approved=approved,
            )))
    return completes

COMPLETES_DATA = _make_completes()


# ── MongoDB data ──────────────────────────────────────────────────────

MONGO_STUDENTS = [
    MongoStudent(
        id="st-laura-gomez", name="Laura Gómez",
        objectives=["Dominar evaluación neurológica", "Aprobar examen de residencia"],
        preferences=StudentPreferences(format="video", schedule="mañana"),
        metrics=StudentMetrics(fatigue=0.2, attention=0.85),
        progress=StudentProgress(topics_completed=12, current_level="intermedio"),
    ),
    MongoStudent(
        id="st-carlos-ruiz", name="Carlos Ruiz",
        objectives=["Reforzar neuroanatomía", "Mejorar en epilepsia"],
        preferences=StudentPreferences(format="lectura", schedule="noche"),
        metrics=StudentMetrics(fatigue=0.5, attention=0.6),
        progress=StudentProgress(topics_completed=5, current_level="principiante"),
    ),
    MongoStudent(
        id="st-ana-martinez", name="Ana Martínez",
        objectives=["Preparar artículo sobre plasticidad", "Actualización en psicofármacos"],
        preferences=StudentPreferences(format="guia", schedule="tarde"),
        metrics=StudentMetrics(fatigue=0.1, attention=0.95),
        progress=StudentProgress(topics_completed=28, current_level="avanzado"),
    ),
    MongoStudent(
        id="st-diego-vega", name="Diego Vega",
        objectives=["Aprobar neurofisiología", "Entender potencial de acción"],
        preferences=StudentPreferences(format="audio", schedule="mañana"),
        metrics=StudentMetrics(fatigue=0.6, attention=0.45),
        progress=StudentProgress(topics_completed=2, current_level="principiante"),
    ),
    MongoStudent(
        id="st-elena-castro", name="Elena Castro",
        objectives=["Rotación en neurología clínica"],
        preferences=StudentPreferences(format="video", schedule="tarde"),
        metrics=StudentMetrics(fatigue=0.3, attention=0.75),
        progress=StudentProgress(topics_completed=18, current_level="intermedio"),
    ),
]

def _make_sessions():
    sessions = []
    session_id = 1
    for st in MONGO_STUDENTS:
        for _ in range(random.randint(3, 8)):
            activity = random.choice(ACTIVITIES)
            topic = random.choice(CONCEPTS)
            date = (datetime.now() - timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d")
            duration = random.randint(15, 90)
            attempts = random.randint(1, 3)
            accuracy = round(random.uniform(40, 100), 1)
            sessions.append(StudySession(
                session_id=f"ses-{session_id:03d}", student_id=st.id, date=date,
                activity=activity.name, topic=topic.name,
                duration_minutes=duration, attempts=attempts, accuracy_percentage=accuracy,
            ))
            session_id += 1
    return sessions

STUDY_SESSIONS = _make_sessions()

def _make_events():
    events = []
    event_id = 1
    for ses in STUDY_SESSIONS:
        # 1–3 events per session
        for _ in range(random.randint(1, 3)):
            et = random.choice(["vista_contenido", "intento_ejercicio", "evaluacion", "revision", "pausa"])
            diff = random.choice(["básico", "intermedio", "avanzado"])
            dur = random.randint(5, max(6, ses.duration_minutes // random.randint(2, 4)))
            attempts = random.randint(0, 3) if et == "intento_ejercicio" else 0
            correct = random.randint(0, attempts) if attempts else 0
            errors = attempts - correct
            acc = round(correct / attempts * 100, 1) if attempts else 0.0
            status = "completado" if et != "pausa" else random.choice(["completado", "abandonado"])
            events.append(InteractionEvent(
                event_id=f"evt-{event_id:04d}", student_id=ses.student_id, session_id=ses.session_id,
                event_type=et, topic=ses.topic, activity=ses.activity, difficulty=diff,
                duration_minutes=dur, status=status,
                attempts=attempts, correct=correct, errors=errors, accuracy_percentage=acc,
            ))
            event_id += 1
    return events

INTERACTION_EVENTS = _make_events()


# ── Seed logic ─────────────────────────────────────────────────────────

def seed_neo4j(neo: Neo4jService):
    print("=== Neo4j: poblando nodos ===")

    for s in SUBJECTS:
        neo.write("CREATE (:Subject {uid: $uid, name: $name, difficulty_level: $dl})",
                  uid=s.uid, name=s.name, dl=s.difficulty_level)
        print(f"  Subject: {s.name}")

    for c in CONCEPTS:
        neo.write(
            "CREATE (:Concept {uid: $uid, name: $name, description: $desc, difficulty_level: $dl, estimated_time_minutes: $etm, usage_frequency: $uf})",
            uid=c.uid, name=c.name, desc=c.description, dl=c.difficulty_level, etm=c.estimated_time_minutes, uf=c.usage_frequency,
        )
        print(f"  Concept: {c.name}")

    for a in ACTIVITIES:
        neo.write(
            "CREATE (:Activity {uid: $uid, name: $name, description: $desc, type: $type, difficulty: $diff, estimated_time_minutes: $etm, cognitive_load: $cl, max_score: $ms})",
            uid=a.uid, name=a.name, desc=a.description, type=a.type, diff=a.difficulty, etm=a.estimated_time_minutes, cl=a.cognitive_load, ms=a.max_score,
        )
        print(f"  Activity: {a.name}")

    for r in RESOURCES:
        neo.write(
            "CREATE (:Resource {uid: $uid, type: $type, duration: $dur, cognitive_load: $cl, url: $url, optimal_learning_style: $ols})",
            uid=r.uid, type=r.type, dur=r.duration, cl=r.cognitive_load, url=r.url, ols=r.optimal_learning_style,
        )
        print(f"  Resource: {r.type} ({r.uid})")

    for st in NEO_STUDENTS:
        neo.write(
            "CREATE (:Student {uid: $uid, name: $name, mastery_level: $ml, preferred_style: $ps, current_session_id: $csid})",
            uid=st.uid, name=st.name, ml=st.mastery_level, ps=st.preferred_style, csid=st.current_session_id,
        )
        print(f"  Student: {st.name}")

    print("\n=== Neo4j: poblando relaciones ===")

    # BELONGS_TO
    for cuid, (suid, weight) in CONCEPT_SUBJECT_MAP.items():
        neo.write(
            "MATCH (c:Concept {uid: $cuid}) MATCH (s:Subject {uid: $suid}) MERGE (c)-[b:BELONGS_TO]->(s) SET b.weight_in_subject = $w",
            cuid=cuid, suid=suid, w=weight,
        )
        print(f"  BELONGS_TO: {cuid} → {suid}")

    # REQUIRES
    for advanced, prereq, weight, level, notes in CONCEPT_REQUIRES:
        neo.write(
            "MATCH (c:Concept {uid: $cuid}) MATCH (p:Concept {uid: $puid}) MERGE (c)-[r:REQUIRES]->(p) SET r.weight = $w, r.level = $l, r.notes = $n",
            cuid=advanced, puid=prereq, w=weight, l=level, n=notes,
        )
        print(f"  REQUIRES: {advanced} → {prereq}")

    # CORRELATES_WITH
    for a_uid, b_uid, strength in CONCEPT_CORRELATIONS:
        neo.write(
            "MATCH (a:Concept {uid: $auid}) MATCH (b:Concept {uid: $buid}) MERGE (a)-[r:CORRELATES_WITH]->(b) SET r.strength = $s",
            auid=a_uid, buid=b_uid, s=strength,
        )
        print(f"  CORRELATES_WITH: {a_uid} → {b_uid}")

    # DEEPENS
    for advanced, found, factor in CONCEPT_DEEPENS:
        neo.write(
            "MATCH (adv:Concept {uid: $auid}) MATCH (found:Concept {uid: $fuid}) MERGE (adv)-[r:DEEPENS]->(found) SET r.complexity_factor = $cf",
            auid=advanced, fuid=found, cf=factor,
        )
        print(f"  DEEPENS: {advanced} → {found}")

    # ALTERNATIVE_TO
    for c_uid, alt_uid, cost, style in CONCEPT_ALTERNATIVES:
        neo.write(
            "MATCH (c:Concept {uid: $cuid}) MATCH (alt:Concept {uid: $auid}) MERGE (c)-[r:ALTERNATIVE_TO]->(alt) SET r.additional_cost = $ac, r.favored_style = $fs",
            cuid=c_uid, auid=alt_uid, ac=cost, fs=style,
        )
        print(f"  ALTERNATIVE_TO: {c_uid} → {alt_uid}")

    # EVALUATES
    for auid, suid, coverage, threshold in ACTIVITY_SUBJECT_MAP:
        neo.write(
            "MATCH (a:Activity {uid: $auid}) MATCH (s:Subject {uid: $suid}) MERGE (a)-[e:EVALUATES]->(s) SET e.coverage = $cov, e.approval_threshold = $at",
            auid=auid, suid=suid, cov=coverage, at=threshold,
        )
        print(f"  EVALUATES: {auid} → {suid}")

    # EXPLAINS
    for ruid, cuid, coverage in RESOURCE_CONCEPT_MAP:
        neo.write(
            "MATCH (r:Resource {uid: $ruid}) MATCH (c:Concept {uid: $cuid}) MERGE (r)-[e:EXPLAINS]->(c) SET e.coverage = $cov",
            ruid=ruid, cuid=cuid, cov=coverage,
        )
        print(f"  EXPLAINS: {ruid} → {cuid}")

    # STUDIES
    for suid, cuid, rel in STUDIES_DATA:
        neo.write(
            "MATCH (s:Student {uid: $suid}) MATCH (c:Concept {uid: $cuid}) MERGE (s)-[r:STUDIES]->(c) SET r.total_time_minutes = $ttm, r.last_studied_at = datetime(), r.times_studied = $ts, r.mastery_level = $ml",
            suid=suid, cuid=cuid, ttm=rel.total_time_minutes, ts=rel.times_studied, ml=rel.mastery_level,
        )
        print(f"  STUDIES: {suid} → {cuid}")

    # COMPLETES
    for suid, auid, rel in COMPLETES_DATA:
        neo.write(
            "MATCH (s:Student {uid: $suid}) MATCH (a:Activity {uid: $auid}) MERGE (s)-[r:COMPLETES]->(a) SET r.score_obtained = $so, r.time_taken_seconds = $tts, r.completed_at = datetime(), r.attempts = $att, r.approved = $app",
            suid=suid, auid=auid, so=rel.score_obtained, tts=rel.time_taken_seconds, att=rel.attempts, app=rel.approved,
        )
        print(f"  COMPLETES: {suid} → {auid}")


def seed_mongo(mongo: MongoService):
    db = mongo.db
    print("\n=== MongoDB: poblando colecciones ===")

    estudiantes = db["estudiantes"]
    for st in MONGO_STUDENTS:
        estudiantes.insert_one(st.model_dump())
        print(f"  Student: {st.name}")

    sesiones = db["sesiones_estudio"]
    for ses in STUDY_SESSIONS:
        sesiones.insert_one(ses.model_dump())
    print(f"  StudySessions: {len(STUDY_SESSIONS)} insertadas")

    eventos = db["eventos_interaccion"]
    for evt in INTERACTION_EVENTS:
        eventos.insert_one(evt.model_dump())
    print(f"  InteractionEvents: {len(INTERACTION_EVENTS)} insertadas")


def main():
    mongo = MongoService(settings.mongo_uri)
    neo4j = Neo4jService(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)

    with mongo, neo4j:
        # Clean existing data
        print("Limpiando datos existentes...")
        neo4j.write("MATCH (n) DETACH DELETE n")
        mongo.db["estudiantes"].delete_many({})
        mongo.db["sesiones_estudio"].delete_many({})
        mongo.db["eventos_interaccion"].delete_many({})
        print("Bases limpias.\n")

        seed_neo4j(neo4j)
        seed_mongo(mongo)

    print("\nSeed completado.")


if __name__ == "__main__":
    main()
