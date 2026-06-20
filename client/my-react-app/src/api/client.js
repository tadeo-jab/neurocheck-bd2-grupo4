const BASE = "";

function getToken() {
  return localStorage.getItem("token");
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Error ${res.status}`);
  }
  return res.json();
}

export const api = {
  // ── Auth ────────────────────────────────────────────────
  login(email, password) {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  register(email, password, nombre, estilo_preferido) {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, nombre, estilo_preferido }),
    });
  },

  me() {
    return request("/auth/me");
  },

  logout() {
    return request("/auth/logout", { method: "POST" });
  },

  // ── Curriculum ──────────────────────────────────────────
  getEnrollments(estudianteId) {
    return request(`/curriculum/enrollments/${estudianteId}`);
  },

  getTree(estudianteId) {
    return request(`/curriculum/tree/${estudianteId}`);
  },

  getSubjectTree(materiaId, estudianteId) {
    return request(
      `/curriculum/subject/${materiaId}/tree?id_estudiante=${estudianteId}`
    );
  },

  enroll(estudianteId, materiaId) {
    return request("/curriculum/enroll", {
      method: "POST",
      body: JSON.stringify({
        id_estudiante: estudianteId,
        id_materia: materiaId,
      }),
    });
  },

  // ── Study ───────────────────────────────────────────────
  getCourse(materiaId, estudianteId) {
    return request(
      `/study/subject/${materiaId}/course?id_estudiante=${estudianteId}`
    );
  },

  startAttempt(materiaId, contenidoId, tipoContenido, duracionTotal = 0) {
    return request("/study/attempt/start", {
      method: "POST",
      body: JSON.stringify({
        id_materia: materiaId,
        id_contenido: contenidoId,
        tipo_contenido: tipoContenido,
        duracion_total: duracionTotal,
      }),
    });
  },

  pauseAttempt(intentoId) {
    return request(`/study/attempt/${intentoId}/pause`, { method: "POST" });
  },

  resumeAttempt(intentoId) {
    return request(`/study/attempt/${intentoId}/resume`, { method: "POST" });
  },

  closeAttempt(intentoId, data = {}) {
    return request(`/study/attempt/${intentoId}/close`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // ── Mates ───────────────────────────────────────────────
  getMates(estudianteId) {
    return request(`/mates/${estudianteId}`);
  },

  getSuggestedMates(estudianteId) {
    return request(`/mates/${estudianteId}/suggested`);
  },

  sendMateRequest(studentIdA, studentIdB) {
    return request("/mates/request", {
      method: "POST",
      body: JSON.stringify({
        student_id_a: studentIdA,
        student_id_b: studentIdB,
      }),
    });
  },
};
