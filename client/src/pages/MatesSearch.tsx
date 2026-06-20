import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

interface SuggestedMate {
  id: string
  nombre: string
  puntaje: number
}

export default function MatesSearch() {
  const user = JSON.parse(localStorage.getItem('user') ?? '{}')
  const [mates, setMates] = useState<SuggestedMate[]>([])
  const [requested, setRequested] = useState<Set<string>>(new Set())

  useEffect(() => {
    fetch(`/api/mates/${user.id}/suggested`)
      .then((res) => res.json())
      .then((data) => setMates(data))
      .catch(() => setMates([]))
  }, [user.id])

  const handleRequest = (mateId: string) => {
    fetch('/api/mates/request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_id_a: user.id, student_id_b: mateId }),
    }).then((res) => {
      if (res.ok) setRequested((prev) => new Set(prev).add(mateId))
    })
  }

  return (
    <div style={{ padding: 24 }}>
      <Link to="/">← Volver</Link>
      <h1>Compañeros recomendados</h1>
      {mates.length === 0 && <p>No hay sugerencias por ahora</p>}
      <ul>
        {mates.map((mate) => (
          <li key={mate.id} style={{ marginBottom: 8 }}>
            {mate.nombre}
            <span style={{ color: '#888', marginLeft: 8 }}>
              ({mate.puntaje} pts)
            </span>
            {requested.has(mate.id) ? (
              <span style={{ color: 'green', marginLeft: 8 }}>Solicitado</span>
            ) : (
              <button
                onClick={() => handleRequest(mate.id)}
                style={{ marginLeft: 8 }}
              >
                Enviar solicitud
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
