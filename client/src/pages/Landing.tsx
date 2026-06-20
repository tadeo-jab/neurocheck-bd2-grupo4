import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

interface Mate {
  estudiante: { id: string; nombre: string; estilo_preferido?: string }
  aceptado: boolean
}

interface Materia {
  id: string
  nombre: string
  descripcion: string
  nivel_dificultad: number
  tiempo_estimado: number
  frecuencia_uso: string
}

export default function Landing() {
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') ?? '{}')
  const [mates, setMates] = useState<Mate[]>([])
  const [cursos, setCursos] = useState<Materia[]>([])

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) {
      navigate('/login')
      return
    }
    fetch(`/api/mates/${user.id}`)
      .then((res) => res.json())
      .then((data) => setMates(data))
      .catch(() => setMates([]))

    fetch(`/api/curriculum/enrollments/${user.id}`)
      .then((res) => res.json())
      .then((data) => setCursos(data))
      .catch(() => setCursos([]))
  }, [navigate, user.id])

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <aside style={{ width: 220, borderRight: '1px solid #ccc', padding: 16 }}>
        <h2>Amigos</h2>
        {mates.length === 0 && <p>No tenes amigos todavía</p>}
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {mates.map((mate) => (
            <li
              key={mate.estudiante.id}
              style={{ padding: '4px 0', opacity: mate.aceptado ? 1 : 0.5 }}
            >
              {mate.estudiante.nombre}
              {!mate.aceptado && ' (pendiente)'}
            </li>
          ))}
        </ul>
        <Link to="/mates-search" style={{ display: 'block', marginTop: 12 }}>
          Buscar compañeros
        </Link>
      </aside>
      <main style={{ flex: 1, padding: 24 }}>
        <h1>Mis cursos</h1>
        {cursos.length === 0 && <p>No estas anotado en ninguna materia</p>}
        <ul>
          {cursos.map((materia) => (
            <li key={materia.id} style={{ marginBottom: 16 }}>
              <Link
                to="/course"
                state={materia}
                style={{ color: 'inherit', textDecoration: 'none' }}
              >
                <strong>{materia.nombre}</strong>
                <p style={{ margin: '4px 0', color: '#555' }}>{materia.descripcion}</p>
                <span style={{ fontSize: 14, color: '#888' }}>
                  Dificultad: {materia.nivel_dificultad} | {materia.tiempo_estimado}h | {materia.frecuencia_uso}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </main>
      <button
        onClick={() => {
          const token = localStorage.getItem('token')
          fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
          }).finally(() => {
            localStorage.clear()
            navigate('/login')
          })
        }}
        style={{
          position: 'fixed',
          top: 24,
          right: 24,
          padding: '10px 20px',
          background: '#757575',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          cursor: 'pointer',
          fontWeight: 'bold',
        }}
      >
        Cerrar sesión
      </button>
      <Link
        to="/tree"
        style={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          padding: '10px 20px',
          background: '#1976d2',
          color: 'white',
          textDecoration: 'none',
          borderRadius: 8,
        }}
      >
        Ver todos los cursos
      </Link>
      <Link
        to="/admin"
        style={{
          position: 'fixed',
          bottom: 24,
          left: 24,
          padding: '10px 20px',
          background: '#757575',
          color: 'white',
          textDecoration: 'none',
          borderRadius: 8,
        }}
      >
        Admin
      </Link>
    </div>
  )
}
