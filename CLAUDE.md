# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment & commands

- Python virtual environment at `env/`. Activate: `source env/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Start databases: `docker compose up -d`
- Wait for healthy containers before connecting: `docker compose ps` (both services should show healthy)
- Python entry point lives at `src/main.py` (run with `python src/main.py`)

## Config

`src/config.py` — Pydantic `Settings` with env prefix `NEUROCHECK_` and optional `.env` file. Defaults match docker-compose credentials for local dev. Config keys: `mongo_uri`, `neo4j_uri`, `neo4j_user`, `neo4j_password`.

## Architecture

Layered dual-database project for a clinical/learning platform ("NeuroCheck"). Layers flow top-down: **services → repositories → db connectors**. Pydantic models sit alongside as shared types.

### DB layer (`src/db/`)

Thin wrappers over the drivers — no CRUD helpers, no business logic:

- **`MongoService`** — wraps `pymongo.MongoClient`. Exposes `self.db` (a `pymongo.database.Database`). Context-manager via `__enter__`/`__exit__`.
- **`Neo4jService`** — wraps `neo4j.GraphDatabase.driver`. Exposes `read(query, **params)` and `write(query, **params)` for transactional work. Context-manager via `__enter__`/`__exit__`.

### Models (`src/models/`)

Pydantic v2 models mirroring the domain entities. `learning.py` holds Neo4j node models (`Student`, `Concept`, `Activity`, `Resource`, `Subject`) and relationship property models (`Learns`, `Completes`, `PrerequisiteOf`, `Uses`, `BelongsTo`). `session.py` holds MongoDB document models (`Session`, `StudentConfig`).

### Repositories (`src/repositories/`)

One repo class per collection/node-type/relationship. All take a driver/database in their constructor — they do not create connections themselves.

- `mongo/` — `SessionRepository`, `StudentConfigRepository` (operate on `pymongo` collections)
- `neo4j/nodes/` — `StudentNodeRepo`, `ConceptNodeRepo`, `ActivityNodeRepo`, `ResourceNodeRepo`, `SubjectNodeRepo` (CREATE/MATCH/DELETE Cypher)
- `neo4j/relationships/` — `LearnsRepo`, `CompletesRepo`, `PrerequisiteOfRepo`, `UsesRepo`, `BelongsToRepo` (MERGE/DELETE relationship Cypher)

### Services (`src/services/`)

Orchestrate repos into higher-level operations:

- **`SessionService`** — `start_session()`, `log_event()` using Mongo repos
- **`LearningService`** — `enroll_in_concept()` using Neo4j repos (wires Student+Concept nodes and Learns relationship)

## Docker Compose

`docker-compose.yml` defines a custom network `neurocheck-network` with two services:

| Service | Image  | Ports                  | Auth                          |
|---------|--------|------------------------|-------------------------------|
| mongo   | mongo:7 | 27017                  | neurocheckMongo / neurocheck  |
| neo4j   | neo4j:5 | 7474 (HTTP), 7687 (Bolt) | neo4j / neurocheck          |

Both use named volumes (`mongo_data`, `neo4j_data`) and healthchecks.
