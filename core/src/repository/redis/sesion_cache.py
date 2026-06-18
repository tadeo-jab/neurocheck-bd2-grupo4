import redis


class SessionCacheRepository:
    _TTL_SESION = 7200       # 2 horas
    _TTL_INTENTOS = 900      # 15 minutos
    _MAX_INTENTOS = 5

    def __init__(self, redis_url: str):
        self._redis = redis.from_url(redis_url, decode_responses=True)

    # ── Sesión ──────────────────────────────────────────────

    def crear_sesion(self, token: str, user_data: dict) -> None:
        self._redis.hset(f"sesiones:sesion:{token}", mapping=user_data)
        self._redis.expire(f"sesiones:sesion:{token}", self._TTL_SESION)

    def vincular_usuario(self, user_id: str, token: str) -> None:
        self._redis.setex(f"sesiones:usuario:{user_id}", self._TTL_SESION, token)

    #Renovar token
    def validar_sesion(self, token: str) -> dict | None:
        datos = self._redis.hgetall(f"sesiones:sesion:{token}")
        if not datos:
            return None
        # Renovar TTL en ambos
        self._redis.expire(f"sesiones:sesion:{token}", self._TTL_SESION)
        user_id = datos.get("user_id")
        if user_id:
            self._redis.expire(f"sesiones:usuario:{user_id}", self._TTL_SESION)
        return datos

    def cerrar_sesion(self, token: str, user_id: str) -> None:
        self._redis.delete(f"sesiones:sesion:{token}", f"sesiones:usuario:{user_id}")

    # ── Intentos fallidos ──────────────────────────────────

    def incrementar_intento(self, email: str) -> int:
        intentos = self._redis.incr(f"sesiones:intentos:{email}")
        self._redis.expire(f"sesiones:intentos:{email}", self._TTL_INTENTOS)
        return intentos

    def intentos_restantes(self, email: str) -> int:
        actual = self._redis.get(f"sesiones:intentos:{email}")
        intentos = int(actual) if actual else 0
        return max(0, self._MAX_INTENTOS - intentos)


