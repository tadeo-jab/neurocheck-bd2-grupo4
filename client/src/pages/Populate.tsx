import { useState } from 'react'
import { Link } from 'react-router-dom'

const DEFAULT_ESTUDIANTES = JSON.stringify([
  { id: 'est-001', nombre: 'Juan Pérez', email: 'juan@mail.com', password: '123456', estilo: 'visual' },
  { id: 'est-002', nombre: 'María Gómez', email: 'maria@mail.com', password: '123456', estilo: 'auditivo' },
  { id: 'est-003', nombre: 'Pedro Ruiz', email: 'pedro@mail.com', password: '123456', estilo: 'kinestésico' },
  { id: 'est-004', nombre: 'Ana López', email: 'ana@mail.com', password: '123456', estilo: 'textual' },
], null, 2)

const DEFAULT_MATERIAS = JSON.stringify([
  { id: 'mat-prog', nombre: 'Introducción a la Programación', desc: 'Variables, control de flujo, funciones y OOP básico.', diff: 1.0, horas: 60, frec: 'trimestral' },
  { id: 'mat-prog-ii', nombre: 'Programación II', desc: 'POO avanzada, patrones de diseño, testing y buenas prácticas.', diff: 2.0, horas: 80, frec: 'trimestral' },
  { id: 'mat-estruc', nombre: 'Estructuras de Datos', desc: 'Listas, pilas, colas, árboles, grafos y análisis de complejidad.', diff: 2.0, horas: 80, frec: 'trimestral' },
  { id: 'mat-fund', nombre: 'Fundamentos de Datos', desc: 'Modelado, normalización, SQL básico y álgebra relacional.', diff: 1.5, horas: 60, frec: 'trimestral' },
  { id: 'mat-fund-ii', nombre: 'Fundamentos de Datos II', desc: 'Modelado avanzado, álgebra relacional aplicada y tuning de queries.', diff: 2.5, horas: 70, frec: 'trimestral' },
  { id: 'mat-bdrel', nombre: 'Bases de Datos Relacionales', desc: 'PostgreSQL, índices, transacciones, ACID, optimización de consultas.', diff: 2.5, horas: 80, frec: 'semestral' },
  { id: 'mat-bdrel-ii', nombre: 'Bases de Datos Relacionales II', desc: 'Replicación, particionamiento, PL/pgSQL y administración avanzada.', diff: 3.5, horas: 90, frec: 'semestral' },
  { id: 'mat-bdnosql', nombre: 'Bases de Datos NoSQL', desc: 'MongoDB, Neo4j — modelado y casos de uso.', diff: 3.0, horas: 70, frec: 'semestral' },
  { id: 'mat-mineria', nombre: 'Minería de Datos', desc: 'Preprocesamiento, clustering, clasificación y reglas de asociación.', diff: 3.5, horas: 90, frec: 'semestral' },
  { id: 'mat-ml', nombre: 'Machine Learning', desc: 'Regresión, árboles de decisión, SVM, redes neuronales y ensambles.', diff: 4.0, horas: 100, frec: 'semestral' },
  { id: 'mat-viz', nombre: 'Visualización de Datos', desc: 'Tableau, matplotlib, dashboards interactivos y storytelling.', diff: 1.5, horas: 50, frec: 'trimestral' },
  { id: 'mat-ingav', nombre: 'Ingeniería de Datos Avanzada', desc: 'Pipelines ETL, data lakes, Kafka, Airflow y arquitecturas cloud.', diff: 4.5, horas: 120, frec: 'anual' },
], null, 2)

const DEFAULT_PRERREQUISITOS = JSON.stringify([
  ['mat-prog-ii', 'mat-prog', 1.0, true, true],
  ['mat-fund-ii', 'mat-fund', 1.0, true, true],
  ['mat-bdrel-ii', 'mat-bdrel', 1.0, true, true],
  ['mat-estruc', 'mat-prog', 1.0, true, false],
  ['mat-bdrel', 'mat-fund', 1.0, true, false],
  ['mat-bdnosql', 'mat-bdrel', 0.8, true, false],
  ['mat-mineria', 'mat-bdrel', 0.6, true, false],
  ['mat-ml', 'mat-mineria', 0.9, true, false],
  ['mat-ml', 'mat-estruc', 0.7, true, false],
  ['mat-viz', 'mat-fund', 0.4, true, false],
  ['mat-ingav', 'mat-ml', 1.0, true, false],
  ['mat-ingav', 'mat-bdnosql', 0.8, true, false],
], null, 2)

const textareaStyle: React.CSSProperties = {
  width: '100%',
  height: 200,
  fontFamily: 'monospace',
  fontSize: 12,
  padding: 8,
  border: '1px solid #ccc',
  borderRadius: 4,
  resize: 'vertical',
}

export default function Populate() {
  const [estudiantes, setEstudiantes] = useState(DEFAULT_ESTUDIANTES)
  const [materias, setMaterias] = useState(DEFAULT_MATERIAS)
  const [prerrequisitos, setPrerrequisitos] = useState(DEFAULT_PRERREQUISITOS)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [ok, setOk] = useState(false)

  const handleSubmit = () => {
    setLoading(true)
    setError('')
    setOk(false)

    let parsedEstudiantes, parsedMaterias, parsedPrerrequisitos
    try { parsedEstudiantes = JSON.parse(estudiantes) } catch {
      setError('JSON inválido en Estudiantes')
      setLoading(false)
      return
    }
    try { parsedMaterias = JSON.parse(materias) } catch {
      setError('JSON inválido en Materias')
      setLoading(false)
      return
    }
    try { parsedPrerrequisitos = JSON.parse(prerrequisitos) } catch {
      setError('JSON inválido en Prerrequisitos')
      setLoading(false)
      return
    }

    fetch('/api/admin/populate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        estudiantes: parsedEstudiantes,
        materias: parsedMaterias,
        prerrequisitos: parsedPrerrequisitos,
      }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        setOk(true)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
      <Link to="/admin">← Volver a Admin</Link>
      <h1>Populate</h1>
      <p style={{ color: '#666', marginBottom: 24 }}>
        Ingresá los datos en formato JSON y presioná <strong>Ejecutar</strong> para popular las bases de datos.
      </p>

      {error && (
        <p style={{ color: '#d32f2f', background: '#ffebee', padding: 12, borderRadius: 4, marginBottom: 16 }}>
          {error}
        </p>
      )}
      {ok && (
        <p style={{ color: '#388e3c', background: '#e8f5e9', padding: 12, borderRadius: 4, marginBottom: 16 }}>
          ✓ Bases de datos pobladas correctamente.
        </p>
      )}

      <div style={{ marginBottom: 20 }}>
        <h3>Estudiantes</h3>
        <textarea
          value={estudiantes}
          onChange={(e) => setEstudiantes(e.target.value)}
          style={textareaStyle}
        />
      </div>

      <div style={{ marginBottom: 20 }}>
        <h3>Materias</h3>
        <textarea
          value={materias}
          onChange={(e) => setMaterias(e.target.value)}
          style={textareaStyle}
        />
      </div>

      <div style={{ marginBottom: 20 }}>
        <h3>Prerrequisitos</h3>
        <textarea
          value={prerrequisitos}
          onChange={(e) => setPrerrequisitos(e.target.value)}
          style={textareaStyle}
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading}
        style={{
          padding: '12px 32px',
          background: '#388e3c',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          cursor: 'pointer',
          fontWeight: 'bold',
          fontSize: 16,
          opacity: loading ? 0.6 : 1,
        }}
      >
        {loading ? 'Poblando...' : 'Ejecutar'}
      </button>
    </div>
  )
}
