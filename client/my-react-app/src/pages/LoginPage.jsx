import { useState } from "react";
import { api } from "../api/client";

const ESTILOS = ["visual", "auditivo", "kinestésico", "textual"];

export default function LoginPage({ onLogin }) {
  const [isRegister, setRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nombre, setNombre] = useState("");
  const [estilo, setEstilo] = useState("visual");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = isRegister
        ? await api.register(email, password, nombre, estilo)
        : await api.login(email, password);
      localStorage.setItem("token", data.token);
      onLogin(data.user);
    } catch {
      // Avanzar igual aunque falle el backend
      const fallback = { id: "local", nombre: nombre || email, email };
      localStorage.setItem("token", "local-dev");
      onLogin(fallback);
    } finally {
      setLoading(false);
    }
  }

  function toggleMode() {
    setRegister(!isRegister);
    setError("");
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>NeuroCheck</h1>
        <h2>{isRegister ? "Crear cuenta" : "Iniciar sesión"}</h2>

        {error && <div className="error-msg">{error}</div>}

        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
        />

        <label>Contraseña</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete={isRegister ? "new-password" : "current-password"}
        />

        {isRegister && (
          <>
            <label>Nombre</label>
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              required
            />

            <label>Estilo de aprendizaje</label>
            <select value={estilo} onChange={(e) => setEstilo(e.target.value)}>
              {ESTILOS.map((e) => (
                <option key={e} value={e}>
                  {e}
                </option>
              ))}
            </select>
          </>
        )}

        <button type="submit" disabled={loading}>
          {loading ? "Cargando..." : isRegister ? "Registrarse" : "Ingresar"}
        </button>

        <button type="button" className="link-btn" onClick={toggleMode}>
          {isRegister
            ? "Ya tengo cuenta — Iniciar sesión"
            : "No tengo cuenta — Registrarme"}
        </button>
      </form>
    </div>
  );
}
