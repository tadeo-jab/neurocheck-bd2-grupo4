import { useState, useEffect, useRef } from "react";

const QUIZ = {
  nombre: "Evaluación diagnóstica",
  preguntas: [
    {
      id: 1,
      texto: "¿Cuál es la derivada de f(x) = x²?",
      opciones: ["x", "2x", "x²", "2"],
      correcta: 1,
    },
    {
      id: 2,
      texto: "¿Qué estructura de datos usa FIFO?",
      opciones: ["Pila", "Cola", "Árbol", "Grafo"],
      correcta: 1,
    },
    {
      id: 3,
      texto: "¿Cuál es la media de [2, 4, 6, 8]?",
      opciones: ["4", "5", "6", "8"],
      correcta: 1,
    },
    {
      id: 4,
      texto: "¿Qué palabra clave define una función en Python?",
      opciones: ["func", "def", "fn", "lambda"],
      correcta: 1,
    },
    {
      id: 5,
      texto: "¿Cuál es el resultado de 2³?",
      opciones: ["6", "8", "9", "4"],
      correcta: 1,
    },
  ],
};

function formatTime(secs) {
  const m = String(Math.floor(secs / 60)).padStart(2, "0");
  const s = String(secs % 60).padStart(2, "0");
  return `${m}:${s}`;
}

export default function ActivityPage({ user, subjectName, onNavigate }) {
  const TOTAL = 30 * 60; // 30 minutos

  const [remaining, setRemaining] = useState(TOTAL);
  const [paused, setPaused] = useState(false);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(null);
  const timerRef = useRef(null);

  // ── Timer ────────────────────────────────────────────
  useEffect(() => {
    if (!paused && remaining > 0 && !submitted) {
      timerRef.current = setInterval(
        () => setRemaining((r) => (r <= 1 ? 0 : r - 1)),
        1000
      );
    }
    return () => clearInterval(timerRef.current);
  }, [paused, remaining, submitted]);

  // Auto-submit cuando se acaba el tiempo
  useEffect(() => {
    if (remaining === 0 && !submitted) {
      handleSubmit();
    }
  }, [remaining]);

  function handleSubmit() {
    let aciertos = 0;
    QUIZ.preguntas.forEach((p) => {
      if (answers[p.id] === p.correcta) aciertos++;
    });
    const total = QUIZ.preguntas.length;
    setScore({ aciertos, errores: total - aciertos, total });
    setSubmitted(true);
    setPaused(true);
  }

  function handleRetry() {
    setAnswers({});
    setSubmitted(false);
    setScore(null);
    setRemaining(TOTAL);
    setPaused(false);
  }

  const allAnswered =
    Object.keys(answers).length === QUIZ.preguntas.length;

  return (
    <div className="activity-page">
      {/* ── Top bar ──────────────────────────────────── */}
      <header className="topbar">
        <button className="link-btn" onClick={() => onNavigate("landing")}>
          &larr; Volver
        </button>
        <h1>{subjectName} &mdash; {QUIZ.nombre}</h1>

        {/* Timer top-right */}
        <div className="timer-box">
          <span className="timer">{formatTime(remaining)}</span>
          <button
            className={paused ? "primary-btn small" : "secondary-btn small"}
            onClick={() => setPaused(!paused)}
          >
            {paused ? "Reanudar" : "Pausar"}
          </button>
        </div>
      </header>

      {/* ── Main content ─────────────────────────────── */}
      <main className="content-area">
        {submitted ? (
          <div className="attempt-done">
            <h3>Resultado</h3>
            <div className="score-summary">
              <p>Aciertos: {score.aciertos} / {score.total}</p>
              <p>Errores: {score.errores}</p>
              <p>
                {score.aciertos === score.total
                  ? "¡Perfecto!"
                  : score.aciertos >= score.total * 0.6
                    ? "Buen trabajo"
                    : "Seguí practicando"}
              </p>
            </div>
            <p style={{ marginTop: "1rem" }}>
              Tiempo usado: {formatTime(TOTAL - remaining)}
            </p>
            <button className="primary-btn" onClick={handleRetry}>
              Reintentar
            </button>
          </div>
        ) : (
          <div className="quiz">
            {QUIZ.preguntas.map((p) => (
              <div key={p.id} className="quiz-item">
                <p>
                  <strong>
                    {p.id}. {p.texto}
                  </strong>
                </p>
                {p.opciones.map((opt, j) => (
                  <label key={j} className="quiz-option">
                    <input
                      type="radio"
                      name={`q-${p.id}`}
                      value={j}
                      checked={answers[p.id] === j}
                      onChange={() =>
                        setAnswers({ ...answers, [p.id]: j })
                      }
                    />
                    {opt}
                  </label>
                ))}
              </div>
            ))}

            <button
              className="primary-btn"
              disabled={!allAnswered}
              onClick={handleSubmit}
            >
              Enviar respuestas
            </button>
            {!allAnswered && (
              <p className="muted" style={{ marginTop: "0.5rem" }}>
                Respondé todas las preguntas para enviar.
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
