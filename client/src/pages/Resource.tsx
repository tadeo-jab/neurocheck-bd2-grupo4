import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

interface ResourceState {
  id_contenido: string
  id_materia: string
}

interface Precuela {
  id: string
  nombre: string
  descripcion: string
  nivel_dificultad: number
  tiempo_estimado: number
  frecuencia_uso: string
}

interface CloseResult {
  ok: boolean
  warning: boolean
  precuela: Precuela | null
  curso_aprobado: boolean
}

const ESTILOS = ['visual', 'auditivo', 'kinestésico', 'textual']

export default function Resource() {
  const { state } = useLocation()
  const data = state as ResourceState | null
  const token = localStorage.getItem('token') ?? ''
  const user = JSON.parse(localStorage.getItem('user') ?? '{}')

  const navigate = useNavigate()

  const [intentoId, setIntentoId] = useState('')
  const [fileName, setFileName] = useState('')
  const [paused, setPaused] = useState(false)
  const [error, setError] = useState('')

  // Warning / switch flow
  const [showCourseDone, setShowCourseDone] = useState(false)
  const [showWarning, setShowWarning] = useState(false)
  const [precuela, setPrecuela] = useState<Precuela | null>(null)

  useEffect(() => {
    if (!data) return

    fetch('/api/study/attempt/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        id_materia: data.id_materia,
        id_contenido: data.id_contenido,
        tipo_contenido: 'recurso',
        duracion_total: 30,
      }),
    })
      .then(async (res) => {
        if (!res.ok) {
          const msg = await res.text()
          throw new Error(msg || res.statusText)
        }
        return res.json()
      })
      .then((json) => {
        setIntentoId(json.intento_id)
        return fetch(`/api/study/resource/${data.id_contenido}/file`)
      })
      .then(async (res) => {
        if (!res.ok) {
          const msg = await res.text()
          throw new Error(msg || res.statusText)
        }
        const disposition = res.headers.get('Content-Disposition') ?? ''
        const match = disposition.match(/filename="?([^"]+)"?/)
        setFileName(match ? match[1] : data.id_contenido)
      })
      .catch((err) => setError(err.message))
  }, [data, token])

  const togglePause = () => {
    const endpoint = paused ? 'resume' : 'pause'
    fetch(`/api/study/attempt/${intentoId}/${endpoint}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        setPaused(!paused)
      })
      .catch((err) => setError(err.message))
  }

  const handleClose = () => {
    fetch(`/api/study/attempt/${intentoId}/close`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ terminado: true }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        return res.json() as Promise<CloseResult>
      })
      .then((result) => {
        if (result.warning) {
          setPrecuela(result.precuela)
        }
        if (result.curso_aprobado) {
          setShowCourseDone(true)
        } else if (result.warning) {
          setShowWarning(true)
        } else {
          navigate(-1)
        }
      })
      .catch((err) => setError(err.message))
  }

  const dismissCourseDone = () => {
    setShowCourseDone(false)
    if (precuela) {
      setShowWarning(true)
    } else {
      navigate(-1)
    }
  }

  const handleAbandon = () => {
    fetch(`/api/study/attempt/${intentoId}/close`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ terminado: false }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        return res.json() as Promise<CloseResult>
      })
      .then((result) => {
        if (result.warning) {
          setPrecuela(result.precuela)
          setShowWarning(true)
        } else {
          navigate(-1)
        }
      })
      .catch((err) => setError(err.message))
  }

  const handleSwitch = (estilo: string) => {
    fetch('/api/curriculum/switch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id_estudiante: user.id,
        id_materia_old: data!.id_materia,
        id_materia_new: precuela!.id,
        estilo_aprendizaje: estilo,
        sesion_id: localStorage.getItem('sesion_id') ?? '',
      }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        navigate('/')
      })
      .catch((err) => setError(err.message))
  }

  const handleSwitchStyle = (estilo: string) => {
    fetch('/api/curriculum/switch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id_estudiante: user.id,
        id_materia_old: data!.id_materia,
        id_materia_new: data!.id_materia,
        estilo_aprendizaje: estilo,
        sesion_id: localStorage.getItem('sesion_id') ?? '',
      }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        navigate('/')
      })
      .catch((err) => setError(err.message))
  }

  if (!data) {
    return (
      <div style={{ padding: 24 }}>
        <Link to="/">← Volver</Link>
        <p>Recurso no encontrado</p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: 24 }}>
        <Link to="/">← Volver a Mis cursos</Link>
        <h1>Recurso</h1>
        <p style={{ color: 'red' }}>Error: {error}</p>
      </div>
    )
  }

  if (!fileName) {
    return (
      <div style={{ padding: 24 }}>
        <Link to="/">← Volver a Mis cursos</Link>
        <h1>Recurso</h1>
        <p>Cargando...</p>
      </div>
    )
  }

  return (
    <div style={{ padding: 24 }}>
      <Link to="/">← Volver a Mis cursos</Link>
      <h1>{fileName}</h1>
      <div style={{ position: 'fixed', top: 16, right: 16, display: 'flex', gap: 8 }}>
        <button
          onClick={handleAbandon}
          style={{
            padding: '8px 16px',
            background: '#757575',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          Abandonar
        </button>
        <button
          onClick={togglePause}
          style={{
            padding: '8px 16px',
            background: paused ? '#388e3c' : '#f57c00',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          {paused ? '▶ Reanudar' : '⏸ Pausar'}
        </button>
      </div>
      <embed
        src={`/api/study/resource/${data.id_contenido}/file`}
        type="application/pdf"
        style={{ width: '100%', height: '80vh', marginTop: 16 }}
      />
      <div style={{ textAlign: 'center', marginTop: 24 }}>
        <button
          onClick={handleClose}
          style={{
            padding: '10px 32px',
            background: '#d32f2f',
            color: 'white',
            border: 'none',
            borderRadius: 8,
            cursor: 'pointer',
            fontWeight: 'bold',
            fontSize: 16,
          }}
        >
          Finalizar
        </button>
      </div>

      {/* Curso completado popup */}
      {showCourseDone && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              background: 'white',
              padding: 32,
              borderRadius: 12,
              maxWidth: 400,
              textAlign: 'center',
            }}
          >
            <h2 style={{ marginTop: 0, color: '#2e7d32' }}>Felicitaciones</h2>
            <p>Completaste todos los contenidos de esta materia.</p>
            <button
              onClick={dismissCourseDone}
              style={{
                marginTop: 16,
                padding: '8px 24px',
                background: '#1976d2',
                color: 'white',
                border: 'none',
                borderRadius: 8,
                cursor: 'pointer',
              }}
            >
              Continuar
            </button>
          </div>
        </div>
      )}

      {/* Warning popup */}
      {showWarning && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              background: 'white',
              padding: 32,
              borderRadius: 12,
              maxWidth: 400,
              textAlign: 'center',
            }}
          >
            <h2 style={{ marginTop: 0 }}>Te está yendo mal</h2>
            {precuela ? (
              <>
                <p>¿Cambiar a <strong>{precuela.nombre}</strong>?</p>
                <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
                  {ESTILOS.map((estilo) => (
                    <button
                      key={estilo}
                      onClick={() => handleSwitch(estilo)}
                      style={{
                        padding: '8px 16px',
                        background: '#1976d2',
                        color: 'white',
                        border: 'none',
                        borderRadius: 8,
                        cursor: 'pointer',
                        textTransform: 'capitalize',
                      }}
                    >
                      {estilo}
                    </button>
                  ))}
                </div>
                <button
                  onClick={() => navigate(-1)}
                  style={{
                    marginTop: 16,
                    padding: '8px 24px',
                    background: '#ccc',
                    border: 'none',
                    borderRadius: 8,
                    cursor: 'pointer',
                  }}
                >
                  No, gracias
                </button>
              </>
            ) : (
              <>
                <p>¿Cambiar el estilo de aprendizaje de esta materia?</p>
                <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 12 }}>
                  {ESTILOS.map((estilo) => (
                    <button
                      key={estilo}
                      onClick={() => handleSwitchStyle(estilo)}
                      style={{
                        padding: '8px 16px',
                        background: '#1976d2',
                        color: 'white',
                        border: 'none',
                        borderRadius: 8,
                        cursor: 'pointer',
                        textTransform: 'capitalize',
                      }}
                    >
                      {estilo}
                    </button>
                  ))}
                </div>
                <button
                  onClick={() => navigate(-1)}
                  style={{
                    padding: '8px 24px',
                    background: '#ccc',
                    border: 'none',
                    borderRadius: 8,
                    cursor: 'pointer',
                  }}
                >
                  No, gracias
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
