import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

interface MateriaData {
  id: string
  nombre: string
  descripcion: string
  nivel_dificultad: number
  tiempo_estimado: number
  frecuencia_uso: string
}

export default function Subject() {
  const { state } = useLocation()
  const materia = state as MateriaData | null
  const user = JSON.parse(localStorage.getItem('user') ?? '{}')
  const [enrolled, setEnrolled] = useState(false)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [estilo, setEstilo] = useState('visual')

  if (!materia) {
    return (
      <div style={{ padding: 24 }}>
        <Link to="/tree">← Volver</Link>
        <p>Materia no encontrada</p>
      </div>
    )
  }

  const handleEnroll = () => {
    setError('')
    fetch('/api/curriculum/enroll', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id_estudiante: user.id,
        id_materia: materia.id,
        estilo_preferido: estilo,
      }),
    }).then((res) => {
      if (res.ok) {
        setEnrolled(true)
        setShowModal(false)
      } else {
        res.json().then((d) => setError(d.detail ?? 'Error al inscribirse'))
      }
    })
  }

  const overlayStyle: React.CSSProperties = {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.4)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  }

  const modalStyle: React.CSSProperties = {
    background: '#fff',
    padding: 32,
    borderRadius: 12,
    minWidth: 320,
    boxShadow: '0 4px 24px rgba(0,0,0,0.2)',
  }

  return (
    <div style={{ padding: 24 }}>
      <Link to="/tree">← Volver al árbol</Link>
      <h1>{materia.nombre}</h1>
      <p>{materia.descripcion}</p>
      <ul>
        <li>Dificultad: {materia.nivel_dificultad}</li>
        <li>Tiempo estimado: {materia.tiempo_estimado}h</li>
        <li>Frecuencia: {materia.frecuencia_uso}</li>
      </ul>
      <Link to={`/subject-tree/${materia.id}`}>
        Ver materias relacionadas
      </Link>
      <div style={{ marginTop: 16 }}>
        {enrolled ? (
          <span style={{ color: 'green' }}>Inscripto</span>
        ) : (
          <button onClick={() => setShowModal(true)}>Inscribirse</button>
        )}
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>

      {showModal && (
        <div style={overlayStyle} onClick={() => setShowModal(false)}>
          <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
            <h2>Elegí tu estilo de aprendizaje</h2>
            <select
              value={estilo}
              onChange={(e) => setEstilo(e.target.value)}
              style={{ width: '100%', padding: 8, marginTop: 12 }}
            >
              <option value="visual">Visual</option>
              <option value="auditivo">Auditivo</option>
              <option value="kinestésico">Kinestésico</option>
              <option value="textual">Textual</option>
            </select>
            <div style={{ marginTop: 20, display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
              <button onClick={() => setShowModal(false)}>Cancelar</button>
              <button onClick={handleEnroll}>Finalizar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
