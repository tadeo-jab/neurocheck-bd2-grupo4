# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment & commands

- Python virtual environment at `core/venv/`. Activate: `source core/venv/bin/activate`
- Install dependencies: `pip install -r core/requirements.txt`
- Start databases: `docker compose up -d`
- Run backend: `python core/src/main.py` (serves FastAPI on port 8000)
- Run frontend dev: `cd client && npm run dev` (Vite on port 5173, proxies /api to backend)
- Seed data: `python core/seed.py` (populates Mongo + Neo4j with test data)
- Test credentials: `juan@mail.com` / `123456` (all 4 seeded students use same password)

## Config

`core/src/config.py` — Pydantic `Settings` with env prefix `NEUROCHECK_` and optional `.env` file. Defaults match docker-compose credentials for local dev. Config keys: `mongo_uri`, `neo4j_uri`, `neo4j_user`, `neo4j_password`, `redis_url`.

## Architecture

Layered dual-database project for a clinical/learning platform ("NeuroCheck"). Layers flow top-down: **API routers → services → repositories → db connectors**. Pydantic models sit alongside as shared types.

- **Redis** is no longer used by any service. The `redis/` repos and `redis_url` config still exist but are dead code.
- **Sessions** live entirely in MongoDB (`sesiones` collection), including the auth token.
- **No rate limiting** — it was removed from scope.

### DB layer (`core/src/db/`)

- **`MongoService`** — wraps `pymongo.MongoClient`. Exposes `self.db`.
- **`Neo4jService`** — wraps `neo4j.GraphDatabase.driver`. Exposes `read(query, **params)` and `write(query, **params)`.

### Models (`core/src/model/`)

- `collection_models.py` — MongoDB document models: `Estudiante`, `Intento`, `Sesion`, `Recurso`, `Actividad`, `CaminoAprendizaje`, `Pregunta`, `Curriculum`, `EventoInteraccion`
- `relationship_models.py` — Neo4j relationship property models: `Requiere`, `Alternativa`, `Estudio`, `Completo`, `AnotadoEn`, `CompañeroDe`, etc.
- `node_models.py` — Neo4j node models: `Estudiante`, `Materia`, `Recurso`, `Actividad`

### Repositories (`core/src/repository/`)

Every method logs its query to stdout via `print()` with `[Mongo]` or `[Neo4j]` prefix.

**Mongo repos** (`mongo/`):
- `EstudianteMDBRepository` — `find_by_email`, `find_by_id`, `insert`
- `SesionRepository` — `create_session`, `end_session`, `find_by_token`, `find_by_uid`, `add_attempt_session`, `get_current_attempts`, `get_student_sessions`
- `IntentoRepository` — `create_attempt`, `find_by_id`, `pause_attempt`, `resume_attempt`, `close_attempt`, `get_last_attempts`
- `CurriculumRepository` — `get_course_by_style`, `get_resource`, `get_activity`
- `EventoRepository` — `create_event` (generic event logging into `eventos` collection)

**Neo4j repos** (`neo4j/`):
- `EstudianteRepository` — `crear`, `exists_by_id`, `get_mate_by_id`, `request_mate`, `recommend_mates`
- `MateriaRepository` — `get_materia`, `exists_by_id`, `get_all_subjects`, `get_all_subject_edges`, `get_related_subjects`, `get_related_edges`, `get_prequel_if_exists`
- `MateriaEstudianteRepository` — `get_student_nodes_status`, `get_student_currently_enrolled`, `get_enrollment_style`, `set_student_enroll`, `unenroll_student`, `set_enrollment_completed`, `set_studied`, `set_completed`, `is_terminado`, `is_aprobado`

### Services (`core/src/service/`)

- **`AuthService(neo4j, mongo)`** — `login()`, `register()`, `validar_sesion(token)`, `logout()`. Sessions stored in MongoDB with token. No Redis.
- **`StudyService(neo4j, mongo)`** — `start_attempt()`, `pause_attempt()`, `resume_attempt()`, `close_attempt()`, `get_subject_course()`, `get_resource()`, `get_activity()`. All attempt timing (pause/resume) stored directly in MongoDB. On close, score is calculated server-side from user answers (threshold: 60% of max). On content approval, auto-checks if all course contents are done and marks enrollment as completed.
- **`CurriculumService(neo4j, mongo)`** — `get_student_enrollments()`, `get_curriculum_tree()`, `get_subject_tree()`, `enroll_student()`, `switch_enrollment()`. Logs events to `eventos` collection on enroll/switch.
- **`AdminService(mongo)`**, **`MatesService(neo4j)`** — admin CRUD and friend recommendations.

### API routers (`core/src/api/`)

- `auth_router.py` — `/api/auth/*` (login, register, me, logout)
- `study_router.py` — `/api/study/*` (course, resource, activity, attempt start/pause/resume/close)
- `curriculum_router.py` — `/api/curriculum/*` (enrollments, tree, subject-tree, enroll, switch)
- `mates_router.py` — `/api/mates/*`
- `admin_router.py` — `/api/admin/*`

### Frontend (`client/src/`)

React + React Router. Stores `token`, `sesion_id`, `user` in localStorage.
- `Landing.tsx` — main page: course list, friends sidebar, logout button
- `Login.tsx` — login form
- `Course.tsx` — course content sequence with green progress highlighting
- `Resource.tsx` / `Activity.tsx` — content views with pause/resume/abandon/finalize flow. Activities show quiz questions and display score popup on close. Both show "Felicitaciones" popup when course is fully completed.
- `Tree.tsx` / `SubjectTree.tsx` — curriculum graphs using Cytoscape.js. Node colors: blue (no_cursada), purple (cursando), green (aprobada).

## Docker Compose

`docker-compose.yml` defines a custom network `neurocheck-network` with two services:

| Service | Image  | Ports                  | Auth                          |
|---------|--------|------------------------|-------------------------------|
| mongo   | mongo:7 | 27017                  | neurocheckMongo / neurocheck  |
| neo4j   | neo4j:5 | 7474 (HTTP), 7687 (Bolt) | neo4j / neurocheck          |

Both use named volumes (`mongo_data`, `neo4j_data`) and healthchecks.

## Gotchas

- **MongoDB returns naive datetimes**. Always call `.replace(tzinfo=timezone.utc)` after reading datetimes from Mongo before doing arithmetic with `datetime.now(timezone.utc)`.
- The `intento_repository.py` methods `pause_attempt()` and `resume_attempt()` mutate the document in place AND return it — the returned dict has the updated values for immediate use.
- `get_subject_course()` returns `tuple[CaminoAprendizaje, dict[int, bool]]` — the dict maps sequence index to completed/approved status.
- Seed passwords use bcrypt with `bcrypt.gensalt()` — each seed run generates different hashes.
