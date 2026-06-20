import { useState } from 'react'
import { Link } from 'react-router-dom'

interface Estudiante {
  uid: string
  nombre: string
  email: string
  estilo_preferido: string
}

interface Sesion {
  uid: string
  estudiante: Estudiante
  fecha_ini: string
  fecha_fin: string | null
  intentos_estudio: unknown[]
  fatiga_estimada: number
}

interface Intento {
  uid: string
  id_materia: string
  id_contenido: string
  tipo_contenido: string
  inicio: string
  fin: string | null
  duracion_segundos: number
  pausas: number
  terminado: boolean
  aprobado: boolean | null
  puntaje: number | null
}

export default function Admin() {
  const [studentId, setStudentId] = useState('')
  const [sesiones, setSesiones] = useState<Sesion[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [intentos, setIntentos] = useState<Intento[]>([])
  const [error, setError] = useState('')

  const searchSessions = () => {
    setSelectedId(null)
    setIntentos([])
    fetch(`/api/admin/sessions/${studentId}`)
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        return res.json()
      })
      .then((data) => setSesiones(data))
      .catch((err) => setError(err.message))
  }

  const selectSession = (id: string) => {
    setSelectedId(id)
    fetch(`/api/admin/attempts/${id}`)
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        return res.json()
      })
      .then((data) => setIntentos(data))
      .catch((err) => setError(err.message))
  }

  return (
    <div style={{ padding: 24 }}>
      <Link to="/"> Volver a Mis cursos</Link>
      <h1>Admin</h1>

      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        <input
          value={studentId}
          onChange={(e) => setStudentId(e.target.value)}
          placeholder="ID de estudiante"
          style={{ padding: '8px 12px', fontSize: 16, flex: 1, maxWidth: 300 }}
        />
        <button
          onClick={searchSessions}
          style={{
            padding: '8px 24px',
            background: '#1976d2',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          Buscar
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>Error: {error}</p>}

      <div style={{ display: 'flex', gap: 24 }}>
        {/* Sessions list */}
        <div style={{ flex: 1 }}>
          {sesiones.map((s) => (
            <div
              key={s.uid}
              onClick={() => selectSession(s.uid)}
              style={{
                padding: 16,
                marginBottom: 12,
                background: selectedId === s.uid ? '#e3f2fd' : '#f5f5f5',
                border: selectedId === s.uid ? '2px solid #1976d2' : '1px solid #ddd',
                borderRadius: 8,
                cursor: 'pointer',
              }}
            >
              <strong>{s.uid}</strong>
              <p style={{ margin: '4px 0', color: '#555' }}>
                {new Date(s.fecha_ini).toLocaleString()}
                {' '}
                {s.fecha_fin ? ` ${new Date(s.fecha_fin).toLocaleString()}` : ' (activa)'}
              </p>
              <span style={{ fontSize: 14, color: '#888' }}>
                Fatiga: {s.fatiga_estimada} | Intentos: {s.intentos_estudio.length}
              </span>
            </div>
          ))}
          {sesiones.length === 0 && studentId && (
            <p style={{ color: '#888' }}>No se encontraron sesiones</p>
          )}
        </div>

        {/* Attempts panel */}
        {selectedId && (
          <div style={{ flex: 1 }}>
            <h3>Intentos de {selectedId}</h3>
            {intentos.length === 0 && <p style={{ color: '#888' }}>Sin intentos</p>}
            {intentos.map((i) => (
              <div
                key={i.uid}
                style={{
                  padding: 12,
                  marginBottom: 8,
                  background: '#fafafa',
                  border: '1px solid #ddd',
                  borderRadius: 8,
                  fontSize: 14,
                }}
              >
                <strong>{i.uid}</strong>
                <p style={{ margin: '2px 0', color: '#555' }}>
                  Materia: {i.id_materia} | {i.tipo_contenido}: {i.id_contenido}
                </p>
                <p style={{ margin: '2px 0', color: '#555' }}>
                  Inicio: {new Date(i.inicio).toLocaleString()}
                  {i.fin && ` Fin: ${new Date(i.fin).toLocaleString()}`}
                </p>
                <span style={{ color: i.terminado ? '#388e3c' : '#f57c00' }}>
                  {i.terminado ? 'Terminado' : 'En progreso'}
                </span>
                {' '}
                {i.aprobado !== null && (
                  <span style={{ color: i.aprobado ? '#388e3c' : '#d32f2f' }}>
                    {i.aprobado ? 'Aprobado' : 'No aprobado'}
                  </span>
                )}
                {i.puntaje !== null && ` Puntaje: ${i.puntaje}`}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
