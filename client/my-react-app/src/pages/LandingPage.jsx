const MATERIAS = [
  {
    id: "mat1",
    nombre: "Matemáticas",
    descripcion: "Álgebra, cálculo y geometría analítica",
    nivel: 3.5,
    horas: 60,
    progreso: 45,
  },
  {
    id: "mat2",
    nombre: "Programación",
    descripcion: "Estructuras de datos y algoritmos",
    nivel: 4.0,
    horas: 80,
    progreso: 20,
  },
  {
    id: "mat3",
    nombre: "Estadística",
    descripcion: "Probabilidad e inferencia estadística",
    nivel: 3.0,
    horas: 40,
    progreso: 0,
  },
];

const COMPANIEROS = [
  { id: "c1", nombre: "Ana López", estilo: "visual" },
  { id: "c2", nombre: "Carlos Ruiz", estilo: "auditivo" },
  { id: "c3", nombre: "María Gómez", estilo: "kinestésico" },
];

export default function LandingPage({ user, onNavigate, onLogout }) {
  function handleLogout() {
    localStorage.removeItem("token");
    onLogout();
  }

  return (
    <div className="landing-page">
      <header className="topbar">
        <h1>NeuroCheck</h1>
        <div className="topbar-right">
          <span className="user-name">{user.nombre}</span>
          <button className="logout-btn" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </header>

      <main className="dashboard">
        {/* ── Materias ─────────────────────────────────── */}
        <section className="card">
          <h2>Mis materias</h2>
          <ul className="subject-list">
            {MATERIAS.map((m) => (
              <li key={m.id}>
                <div className="subject-info">
                  <strong>{m.nombre}</strong>
                  <span className="muted">
                    Dificultad {m.nivel} &middot; ~{m.horas}h
                  </span>
                  <p>{m.descripcion}</p>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${m.progreso}%` }}
                    />
                  </div>
                  <span className="muted" style={{ fontSize: "0.8rem" }}>
                    {m.progreso}% completado
                  </span>
                </div>
                <button
                  className="primary-btn"
                  onClick={() =>
                    onNavigate("activity", {
                      subjectId: m.id,
                      name: m.nombre,
                    })
                  }
                >
                  Iniciar actividad
                </button>
              </li>
            ))}
          </ul>
        </section>

        {/* ── Progreso curricular ──────────────────────── */}
        <section className="card">
          <h2>Progreso curricular</h2>
          <div className="tree-grid">
            {MATERIAS.map((m) => (
              <div
                key={m.id}
                className={`tree-node ${
                  m.progreso >= 100
                    ? "done"
                    : m.progreso > 0
                      ? "active"
                      : ""
                }`}
              >
                <span className="node-name">{m.nombre}</span>
                <span className="node-badge">
                  {m.progreso >= 100
                    ? "completado"
                    : m.progreso > 0
                      ? "en progreso"
                      : "pendiente"}
                </span>
              </div>
            ))}
          </div>
          <button
            className="secondary-btn"
            style={{ marginTop: "1rem" }}
            onClick={() => onNavigate("graph")}
          >
            Ver mapa
          </button>
        </section>

        {/* ── Compañeros ──────────────────────────────── */}
        <section className="card">
          <h2>Compañeros de estudio</h2>
          <ul className="mates-list">
            {COMPANIEROS.map((c) => (
              <li key={c.id}>
                {c.nombre} &mdash;{" "}
                <span className="muted">{c.estilo}</span>
              </li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  );
}
