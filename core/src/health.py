from dataclasses import dataclass
from time import perf_counter

from config import settings
from db.mongo import MongoService
from db.neo4j import Neo4jService



@dataclass
class HealthResult:
    ok: bool
    mongo_ok: bool
    neo4j_ok: bool
    mongo_ms: float
    neo4j_ms: float
    detail: str

def print_settings():
    print("Current settings:")
    print(f"  mongo_uri: {settings.mongo_uri}")
    print(f"  neo4j_uri: {settings.neo4j_uri}")
    print(f"  neo4j_user: {settings.neo4j_user}")
    print(f"  neo4j_password: {'*' * len(settings.neo4j_password)}")


def check() -> HealthResult:
    print_settings()

    mongo = MongoService(settings.mongo_uri)
    neo4j = Neo4jService(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)

    mongo_ok, mongo_ms = _check_mongo(mongo)
    neo4j_ok, neo4j_ms = _check_neo4j(neo4j)

    ok = mongo_ok and neo4j_ok
    if ok:
        detail = "Both databases healthy"
    else:
        parts = []
        if not mongo_ok:
            parts.append("MongoDB unreachable")
        if not neo4j_ok:
            parts.append("Neo4j unreachable")
        detail = "; ".join(parts)

    return HealthResult(
        ok=ok,
        mongo_ok=mongo_ok,
        neo4j_ok=neo4j_ok,
        mongo_ms=mongo_ms,
        neo4j_ms=neo4j_ms,
        detail=detail,
    )


def _check_mongo(mongo: MongoService) -> tuple[bool, float]:
    t0 = perf_counter()
    try:
        mongo.connect()
        col = mongo.db["_health"]
        doc = {"_health": True, "ping": "pong"}
        col.insert_one(doc)
        found = col.find_one({"ping": "pong"})
        col.delete_many({"_health": True})
        ok = found is not None and found.get("ping") == "pong"
    except Exception as e:
        print(f"[health] MongoDB error: {e}")
        ok = False
    finally:
        mongo.disconnect()
    return ok, round((perf_counter() - t0) * 1000, 2)


def _check_neo4j(neo4j: Neo4jService) -> tuple[bool, float]:
    t0 = perf_counter()
    try:
        neo4j.connect()
        neo4j.write("CREATE (:Health {ping: 'pong'})")
        result = neo4j.read("MATCH (h:Health {ping: 'pong'}) RETURN h.ping AS ping LIMIT 1")
        neo4j.write("MATCH (h:Health) DELETE h")
        ok = len(result) > 0 and result[0]["ping"] == "pong"
    except Exception as e:
        print(f"[health] Neo4j error: {e}")
        ok = False
    finally:
        neo4j.disconnect()
    return ok, round((perf_counter() - t0) * 1000, 2)


if __name__ == "__main__":
    result = check()
    status = "OK" if result.ok else "FAIL"
    print(f"[{status}] {result.detail}")
    print(f"  MongoDB: {'OK' if result.mongo_ok else 'FAIL'} ({result.mongo_ms} ms)")
    print(f"  Neo4j:   {'OK' if result.neo4j_ok else 'FAIL'} ({result.neo4j_ms} ms)")
