import { useState, useEffect } from "react";
import { api } from "./api/client";
import LoginPage from "./pages/LoginPage";
import LandingPage from "./pages/LandingPage";
import ActivityPage from "./pages/ActivityPage";
import GraphPage from "./pages/GraphPage";
import "./App.css";

export default function App() {
  const [page, setPage] = useState("login");
  const [user, setUser] = useState(null);
  const [activityParams, setActivityParams] = useState(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setChecking(false);
      return;
    }
    api
      .me()
      .then((data) => {
        setUser(data);
        setPage("landing");
      })
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setChecking(false));
  }, []);

  function handleLogin(userData) {
    setUser({ id: userData.id, nombre: userData.nombre, email: userData.email });
    setPage("landing");
  }

  function handleLogout() {
    setUser(null);
    setPage("login");
  }

  function handleNavigate(target, params = null) {
    if (target === "activity") setActivityParams(params);
    setPage(target);
  }

  if (checking) return <div className="page-center">Cargando...</div>;

  if (page === "login") return <LoginPage onLogin={handleLogin} />;

  if (page === "activity" && activityParams)
    return (
      <ActivityPage
        user={user}
        subjectId={activityParams.subjectId}
        subjectName={activityParams.name}
        onNavigate={handleNavigate}
      />
    );

  if (page === "graph")
    return <GraphPage onNavigate={handleNavigate} />;

  return (
    <LandingPage
      user={user}
      onNavigate={handleNavigate}
      onLogout={handleLogout}
    />
  );
}
