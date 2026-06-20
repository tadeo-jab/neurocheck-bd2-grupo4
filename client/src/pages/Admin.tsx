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

interface Evento {
  uid: string
  tipo_evento: string
  timestamp: string
  id_usuario: Estudiante
  sesion: { uid: string }
}

type Tab = 'info' | 'sesiones' | 'eventos'

export default function Admin() {
  const [studentId, setStudentId] = useState('')
  const [estudiante, setEstudiante] = useState<Estudiante | null>(null)
  const [sesiones, setSesiones] = useState<Sesion[]>([])
  const [eventos, setEventos] = useState<Evento[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [intentos, setIntentos] = useState<Intento[]>([])
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<Tab>('info')

  const search = () => {
    setSelectedId(null)
    setIntentos([])
    setError('')
    setEstudiante(null)

    Promise.all([
      fetch(`/api/admin/sessions/${studentId}`).then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        return res.json()
      }),
      fetch(`/api/admin/events/${studentId}`).then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        return res.json()
      }),
    ])
      .then(([sessions, events]) => {
        setSesiones(sessions)
        setEventos(events)
        if (sessions.length > 0) {
          setEstudiante(sessions[0].estudiante)
        }
      })
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

  const tabs: { key: Tab; label: string }[] = [
    { key: 'info', label: 'Info' },
    { key: 'sesiones', label: 'Sesiones' },
    { key: 'eventos', label: 'Eventos' },
  ]

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
          onClick={search}
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

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 0, marginBottom: 24 }}>
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            style={{
              padding: '10px 24px',
              background: activeTab === t.key ? '#1976d2' : '#e0e0e0',
              color: activeTab === t.key ? 'white' : '#333',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 'bold',
              borderRadius: 0,
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Info Tab */}
      {activeTab === 'info' && (
        <div>
          {estudiante ? (
            <div
              style={{
                padding: 24,
                background: '#f5f5f5',
                borderRadius: 8,
                border: '1px solid #ddd',
              }}
            >
              <p><strong>Nombre:</strong> {estudiante.nombre}</p>
              <p><strong>Email:</strong> {estudiante.email}</p>
              <p><strong>ID:</strong> {estudiante.uid}</p>
              <p><strong>Estilo preferido:</strong> {estudiante.estilo_preferido}</p>
            </div>
          ) : (
            <p style={{ color: '#888' }}>
              {studentId ? 'Sin datos del estudiante' : 'Busca un estudiante para ver su información'}
            </p>
          )}
        </div>
      )}

      {/* Sesiones Tab */}
      {activeTab === 'sesiones' && (
        <div style={{ display: 'flex', gap: 24 }}>
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
      )}

      {/* Eventos Tab */}
      {activeTab === 'eventos' && (
        <div>
          {eventos.length === 0 && (
            <p style={{ color: '#888' }}>
              {studentId ? 'Sin eventos' : 'Busca un estudiante para ver sus eventos'}
            </p>
          )}
          {eventos.map((e) => (
            <div
              key={e.uid}
              style={{
                padding: 12,
                marginBottom: 8,
                background: '#fafafa',
                border: '1px solid #ddd',
                borderRadius: 8,
                fontSize: 14,
              }}
            >
              <strong style={{ textTransform: 'capitalize' }}>
                {e.tipo_evento.replace(/_/g, ' ')}
              </strong>
              <p style={{ margin: '2px 0', color: '#555' }}>
                {new Date(e.timestamp).toLocaleString()}
              </p>
              <span style={{ color: '#888' }}>Sesión: {e.sesion.uid}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
