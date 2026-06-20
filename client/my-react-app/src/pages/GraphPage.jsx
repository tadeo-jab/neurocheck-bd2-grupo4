import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";

const NODOS = [
  { id: "mat1", nombre: "Matemáticas", estado: "completado" },
  { id: "mat2", nombre: "Programación", estado: "en_progreso" },
  { id: "mat3", nombre: "Estadística", estado: "pendiente" },
  { id: "mat4", nombre: "Álgebra", estado: "completado" },
  { id: "mat5", nombre: "Cálculo", estado: "en_progreso" },
  { id: "mat6", nombre: "Base de Datos", estado: "pendiente" },
  { id: "mat7", nombre: "Machine Learning", estado: "pendiente" },
];

const ARISTAS = [
  { from: "mat4", to: "mat5", label: "prerrequisito" },
  { from: "mat1", to: "mat5", label: "prerrequisito" },
  { from: "mat1", to: "mat2", label: "prerrequisito" },
  { from: "mat1", to: "mat3", label: "prerrequisito" },
  { from: "mat2", to: "mat6", label: "prerrequisito" },
  { from: "mat3", to: "mat7", label: "prerrequisito" },
  { from: "mat2", to: "mat7", label: "prerrequisito" },
  { from: "mat6", to: "mat7", label: "prerrequisito" },
];

const COLORES = {
  completado: "#22c55e",
  en_progreso: "#3b82f6",
  pendiente: "#d1d5db",
};

export default function GraphPage({ onNavigate }) {
  const containerRef = useRef(null);

  useEffect(() => {
    const cy = cytoscape({
      container: containerRef.current,
      elements: [
        ...NODOS.map((n) => ({
          data: { id: n.id, label: n.nombre, estado: n.estado },
        })),
        ...ARISTAS.map((a) => ({
          data: {
            id: `${a.from}-${a.to}`,
            source: a.from,
            target: a.to,
            label: a.label,
          },
        })),
      ],
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "text-valign": "center",
            "text-halign": "center",
            "font-size": "12px",
            "font-weight": "bold",
            color: "#1e3a5f",
            width: 100,
            height: 100,
            "background-color": (ele) => COLORES[ele.data("estado")],
            "border-width": 3,
            "border-color": "#fff",
            shape: "ellipse",
          },
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#9ca3af",
            "target-arrow-color": "#9ca3af",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            label: "data(label)",
            "font-size": "9px",
            color: "#9ca3af",
            "text-rotation": "autorotate",
          },
        },
      ],
      layout: {
        name: "breadthfirst",
        directed: true,
        padding: 20,
        spacingFactor: 1.3,
      },
      wheelSensitivity: 0.3,
      maxZoom: 2,
      minZoom: 0.3,
    });

    return () => cy.destroy();
  }, []);

  return (
    <div className="graph-page">
      <header className="topbar">
        <button className="link-btn" onClick={() => onNavigate("landing")}>
          &larr; Volver
        </button>
        <h1>Mapa curricular</h1>
        <div className="legend">
          <span className="legend-item">
            <span
              className="legend-dot"
              style={{ background: COLORES.completado }}
            />
            Completado
          </span>
          <span className="legend-item">
            <span
              className="legend-dot"
              style={{ background: COLORES.en_progreso }}
            />
            En progreso
          </span>
          <span className="legend-item">
            <span
              className="legend-dot"
              style={{ background: COLORES.pendiente }}
            />
            Pendiente
          </span>
        </div>
      </header>
      <div className="graph-container" ref={containerRef} />
    </div>
  );
}
