from datetime import datetime, timezone

import redis


class IntentoCacheRepository:
    def __init__(self, redis_url: str):
        self._redis = redis.from_url(redis_url, decode_responses=True)

    # ── Claves ─────────────────────────────────────────────

    def _k_cronometro(self, actividad_id: str, user_id: str) -> str:
        return f"actividades:cronometro:{actividad_id}:{user_id}"

    def _k_limite(self, actividad_id: str, user_id: str) -> str:
        return f"actividades:limite:{actividad_id}:{user_id}"

    # ── Cronómetro ─────────────────────────────────────────

    def iniciar_cronometro(self, intento_id: str, actividad_id: str,
                           user_id: str, duracion_total: int) -> None:
        ahora = datetime.now(timezone.utc).isoformat()
        key = self._k_cronometro(actividad_id, user_id)
        self._redis.hset(key, mapping={
            "intento_id": intento_id,
            "duracion_total": str(duracion_total),
            "transcurrido": "0",
            "tiempo_pausado": "0",
            "pausas": "0",
            "inicio": ahora,
            "pausado": "0",
        })
        self._redis.setex(
            self._k_limite(actividad_id, user_id), duracion_total, "1"
        )

    def pausar_cronometro(self, actividad_id: str, user_id: str) -> float:
        key = self._k_cronometro(actividad_id, user_id)
        datos = self._redis.hgetall(key)
        if not datos or datos.get("pausado") == "1":
            return self._restante(datos) if datos else 0

        ahora = datetime.now(timezone.utc)
        ahora_ts = ahora.timestamp()
        inicio_segmento = datetime.fromisoformat(datos["inicio"]).timestamp()
        transcurrido = float(datos["transcurrido"]) + (ahora_ts - inicio_segmento)

        self._redis.hincrby(key, "pausas", 1)
        self._redis.hset(key, mapping={
            "transcurrido": str(transcurrido),
            "inicio": ahora.isoformat(),  # ahora marca cuándo empezó la pausa
            "pausado": "1",
        })
        self._redis.delete(self._k_limite(actividad_id, user_id))
        return float(datos["duracion_total"]) - transcurrido

    def reanudar_cronometro(self, actividad_id: str, user_id: str) -> float:
        key = self._k_cronometro(actividad_id, user_id)
        datos = self._redis.hgetall(key)
        if not datos or datos.get("pausado") != "1":
            return self._restante(datos) if datos else 0

        ahora = datetime.now(timezone.utc)
        ahora_ts = ahora.timestamp()
        inicio_pausa = datetime.fromisoformat(datos["inicio"]).timestamp()
        tiempo_pausado = float(datos["tiempo_pausado"]) + (ahora_ts - inicio_pausa)

        self._redis.hset(key, mapping={
            "inicio": ahora.isoformat(),  # nuevo segmento de actividad
            "tiempo_pausado": str(tiempo_pausado),
            "pausado": "0",
        })

        restante = self._restante({**datos, "inicio": ahora.isoformat(), "pausado": "0"})
        if restante > 0:
            self._redis.setex(self._k_limite(actividad_id, user_id), int(restante), "1")
        return restante

    def obtener_datos(self, actividad_id: str, user_id: str) -> dict | None:
        datos = self._redis.hgetall(self._k_cronometro(actividad_id, user_id))
        return datos if datos else None

    def obtener_restante(self, actividad_id: str, user_id: str) -> float | None:
        datos = self._redis.hgetall(self._k_cronometro(actividad_id, user_id))
        if not datos:
            return None
        return self._restante(datos)

    def detener_cronometro(self, actividad_id: str, user_id: str) -> float:
        restante = self.obtener_restante(actividad_id, user_id)
        self._redis.delete(
            self._k_cronometro(actividad_id, user_id),
            self._k_limite(actividad_id, user_id),
        )
        return restante if restante is not None else 0

    # ── Interno ────────────────────────────────────────────

    def _restante(self, datos: dict) -> float:
        duracion = float(datos["duracion_total"])
        transcurrido = float(datos["transcurrido"])

        if datos.get("pausado") == "1":
            return max(0, duracion - transcurrido)

        inicio = datetime.fromisoformat(datos["inicio"]).timestamp()
        ahora = datetime.now(timezone.utc).timestamp()
        return max(0, duracion - transcurrido - (ahora - inicio))
