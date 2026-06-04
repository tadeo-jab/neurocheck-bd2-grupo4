# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment & commands

- Python virtual environment at `env/`. Activate: `source env/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Start databases: `docker compose up -d`
- Wait for healthy containers before connecting: `docker compose ps` (both services should show healthy)
- Python entry point lives at `src/main.py` (run with `python src/main.py`)

## Architecture

Dual-database project backing a clinical/medical domain ("NeuroCheck"). Two graph/service layers in `src/`:

- **MongoDB 7** — document store (`src/mongo_service.py`). Connection via `pymongo`, auth against `admin` db, default database `neurocheck`. The `MongoService` class wraps `pymongo.MongoClient` with connect/disconnect/session lifecycle and convenience CRUD helpers.

- **Neo4j 5** — graph database (`src/neo4j_service.py`). Connection via `neo4j` driver over Bolt (`bolt://localhost:7687`). The `Neo4jService` class wraps `GraphDatabase.driver` with `connect_session()` for one-shot queries and `write()`/`read()` for transactional work.

Both services follow the same pattern: optional constructor parameters default to docker-compose values, manual `connect()`/`disconnect()`, and context-manager shortcuts for fire-and-forget usage.

## Docker Compose

`docker-compose.yml` defines a custom network `neurocheck-network` with two services:

| Service | Image  | Ports                  | Auth                    |
|---------|--------|------------------------|-------------------------|
| mongo   | mongo:7 | 27017                  | neurocheckMongo/neurocheck |
| neo4j   | neo4j:5 | 7474 (HTTP), 7687 (Bolt) | neo4j/neurocheck        |

Both use named volumes (`mongo_data`, `neo4j_data`) and healthchecks. MongoDB healthcheck pings via `mongosh`, Neo4j via `wget` against its HTTP endpoint.
