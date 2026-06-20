import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

interface MateriaRef {
  id: string
  nombre: string
}

interface ItemSecuencia {
  tipo: 'recurso' | 'actividad'
  id: string
}

interface CaminoAprendizaje {
  nombre: string
  descripcion?: string
  secuencia: ItemSecuencia[]
}

export default function Course() {
  const { state } = useLocation()
  const materia = state as MateriaRef | null
  const user = JSON.parse(localStorage.getItem('user') ?? '{}')

  const [camino, setCamino] = useState<CaminoAprendizaje | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!materia) return
    fetch(`/api/study/course/${materia.id}/${user.id}`)
      .then(async (res) => {
        if (!res.ok) {
          const msg = await res.text()
          throw new Error(msg || res.statusText)
        }
        return res.json()
      })
      .then((data) => setCamino(data))
      .catch((err) => setError(err.message))
  }, [materia, user.id])

  if (!materia) {
    return (
      <div style={{ padding: 24 }}>
        <Link to="/">← Volver</Link>
        <p>Curso no encontrado</p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: 24 }}>
        <Link to="/">← Volver a Mis cursos</Link>
        <h1>{materia.nombre}</h1>
        <p style={{ color: 'red' }}>Error: {error}</p>
      </div>
    )
  }

  if (!camino) {
    return (
      <div style={{ padding: 24 }}>
        <Link to="/">← Volver a Mis cursos</Link>
        <h1>{materia.nombre}</h1>
        <p>Cargando...</p>
      </div>
    )
  }

  return (
    <div style={{ padding: 24 }}>
      <Link to="/">← Volver a Mis cursos</Link>
      <h1>{materia.nombre}</h1>
      {camino.descripcion && <p>{camino.descripcion}</p>}
      <h2>Contenidos</h2>
      <ol>
        {camino.secuencia.map((item) => (
          <li key={item.id} style={{ marginBottom: 8 }}>
            {item.tipo === 'recurso' ? (
              <Link to="/resource" state={{ id_contenido: item.id, id_materia: materia.id }}>
                📄 {item.id}
              </Link>
            ) : (
              <>📝 {item.id}</>
            )}
          </li>
        ))}
      </ol>
    </div>
  )
}