import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

interface ActivityState {
  id_contenido: string
  id_materia: string
}

interface Pregunta {
  uid: string
  texto: string
  opciones: string[]
  respuesta_correcta: number
  puntaje: number
}

interface Actividad {
  uid: string
  nombre: string
  tipo: string
  preguntas: Pregunta[]
  dificultad: number
  puntaje_maximo: number
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
  aprobado: boolean
  puntaje: number | null
  curso_aprobado: boolean
}

const ESTILOS = ['visual', 'auditivo', 'kinestésico', 'textual']

export default function Activity() {
  const { state } = useLocation()
  const data = state as ActivityState | null
  const token = localStorage.getItem('token') ?? ''
  const user = JSON.parse(localStorage.getItem('user') ?? '{}')

  const navigate = useNavigate()

  const [intentoId, setIntentoId] = useState('')
  const [actividad, setActividad] = useState<Actividad | null>(null)
  const [respuestas, setRespuestas] = useState<Record<string, number>>({})
  const [paused, setPaused] = useState(false)
  const [error, setError] = useState('')

  const [closeResult, setCloseResult] = useState<CloseResult | null>(null)
  const [showFeedback, setShowFeedback] = useState(false)
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
        tipo_contenido: 'actividad',
        duracion_total: 0,
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
        return fetch(`/api/study/activity/${data.id_contenido}`)
      })
      .then(async (res) => {
        if (!res.ok) {
          const msg = await res.text()
          throw new Error(msg || res.statusText)
        }
        return res.json()
      })
      .then((act) => setActividad(act))
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

  const handleResponse = (preguntaId: string, opcionIdx: number) => {
    setRespuestas((prev) => ({ ...prev, [preguntaId]: opcionIdx }))
  }

  const handleClose = () => {
    fetch(`/api/study/attempt/${intentoId}/close`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ terminado: true, respuestas }),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        return res.json() as Promise<CloseResult>
      })
      .then((result) => {
        setCloseResult(result)
        if (result.warning) {
          setPrecuela(result.precuela)
        }
        setShowFeedback(true)
      })
      .catch((err) => setError(err.message))
  }

  const dismissFeedback = () => {
    setShowFeedback(false)
    if (closeResult?.curso_aprobado) {
      setShowCourseDone(true)
    } else if (closeResult?.warning) {
      setShowWarning(true)
    } else {
      navigate(-1)
    }
  }

  const dismissCourseDone = () => {
    setShowCourseDone(false)
    if (closeResult?.warning) {
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

  if (!data) {
    return (
      <div style={{ padding: 24 }}>
        <Link to="/">← Volver</Link>
        <p>Actividad no encontrada</p>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{ padding: 24 }}>
        <Link to="/">← Volver a Mis cursos</Link>
        <h1>Actividad</h1>
        <p style={{ color: 'red' }}>Error: {error}</p>
      </div>
    )
  }

  if (!actividad) {
    return (
      <div style={{ padding: 24 }}>
        <Link to="/">← Volver a Mis cursos</Link>
        <h1>Actividad</h1>
        <p>Cargando...</p>
      </div>
    )
  }

  return (
    <div style={{ padding: 24 }}>
      <Link to="/">← Volver a Mis cursos</Link>
      <h1>{actividad.nombre}</h1>
      <p>
        Tipo: {actividad.tipo} | Dificultad: {actividad.dificultad} | Puntaje
        máximo: {actividad.puntaje_maximo}
      </p>

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

      {actividad.preguntas.length > 0 && (
        <div style={{ maxWidth: 600, margin: '0 auto' }}>
          {actividad.preguntas.map((p) => (
            <div key={p.uid} style={{ marginBottom: 24 }}>
              <p style={{ fontWeight: 'bold' }}>{p.texto}</p>
              {p.opciones.map((opcion, idx) => (
                <label
                  key={idx}
                  style={{
                    display: 'block',
                    padding: '8px 12px',
                    marginBottom: 4,
                    background: respuestas[p.uid] === idx ? '#e3f2fd' : '#f5f5f5',
                    borderRadius: 6,
                    cursor: 'pointer',
                  }}
                >
                  <input
                    type="radio"
                    name={p.uid}
                    value={idx}
                    checked={respuestas[p.uid] === idx}
                    onChange={() => handleResponse(p.uid, idx)}
                    style={{ marginRight: 8 }}
                  />
                  {opcion}
                </label>
              ))}
            </div>
          ))}
        </div>
      )}

      {actividad.tipo === 'proyecto' && (
        <div style={{ maxWidth: 600, margin: '24px auto' }}>
          <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold' }}>
            Auto-percepción (1-5)
          </label>
          <input
            type="range"
            min="1"
            max="5"
            defaultValue="3"
            style={{ width: '100%' }}
          />
        </div>
      )}

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

      {/* Feedback popup */}
      {showFeedback && (
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
            <h2 style={{ marginTop: 0, color: closeResult?.aprobado ? '#2e7d32' : '#c62828' }}>
              {closeResult?.aprobado ? 'Aprobado' : 'No aprobado'}
            </h2>
            {closeResult?.puntaje !== null && closeResult?.puntaje !== undefined && (
              <p>Puntaje: <strong>{closeResult.puntaje}</strong></p>
            )}
            <button
              onClick={dismissFeedback}
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
              <button
                onClick={() => navigate(-1)}
                style={{
                  padding: '8px 24px',
                  background: '#1976d2',
                  color: 'white',
                  border: 'none',
                  borderRadius: 8,
                  cursor: 'pointer',
                }}
              >
                Entendido
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
