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

interface ActividadData {
  uid: string
  nombre: string
  tipo: string
  dificultad: number
  puntaje_maximo: number
  preguntas: Pregunta[]
}

interface CloseResult {
  ok: boolean
  warning: boolean
  precuela: { id: string; nombre: string } | null
}

const btn: React.CSSProperties = {
  padding: '8px 20px',
  border: 'none',
  borderRadius: 8,
  cursor: 'pointer',
  fontWeight: 'bold',
  fontSize: 14,
}

export default function Activity() {
  const { state } = useLocation()
  const data = state as ActivityState | null
  const token = localStorage.getItem('token') ?? ''
  const navigate = useNavigate()

  const [actividad, setActividad] = useState<ActividadData | null>(null)
  const [intentoId, setIntentoId] = useState('')
  const [respuestas, setRespuestas] = useState<Record<string, number>>({})
  const [resultado, setResultado] = useState<{
    aciertos: number
    errores: number
    puntaje: number
    aprobado: boolean
  } | null>(null)
  const [error, setError] = useState('')
  const [showWarning, setShowWarning] = useState(false)
  const [precuela, setPrecuela] = useState<{ id: string; nombre: string } | null>(null)

  // 1. Cargar datos de la actividad e iniciar intento
  useEffect(() => {
    if (!data) return

    fetch(`/api/study/activity/${data.id_contenido}`)
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        return res.json() as Promise<ActividadData>
      })
      .then((act) => {
        setActividad(act)
        return fetch('/api/study/attempt/start', {
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
      })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        return res.json()
      })
      .then((json) => setIntentoId(json.intento_id))
      .catch((err) => setError(err.message))
  }, [data, token])

  const handleSelectOpcion = (uid: string, idx: number) => {
    if (resultado) return // no permitir cambios tras enviar
    setRespuestas((prev) => ({ ...prev, [uid]: idx }))
  }

  // 2. Calcular resultado y cerrar intento (quiz)
  const handleSubmitQuiz = () => {
    if (!actividad) return
    let aciertos = 0
    let errores = 0
    let puntaje = 0

    for (const preg of actividad.preguntas) {
      const seleccion = respuestas[preg.uid]
      if (seleccion === undefined) continue
      if (seleccion === preg.respuesta_correcta) {
        aciertos++
        puntaje += preg.puntaje
      } else {
        errores++
      }
    }

    const aprobado = puntaje >= actividad.puntaje_maximo * 0.6
    setResultado({ aciertos, errores, puntaje, aprobado })
    cerrarIntento(aprobado, true, aciertos, errores, puntaje)
  }

  // 3. Cerrar intento para ejercicio/proyecto (auto-evaluación)
  const handleSelfClose = (aprobado: boolean) => {
    cerrarIntento(aprobado, true, undefined, undefined, undefined)
  }

  const handleAbandon = () => {
    cerrarIntento(false, false, undefined, undefined, undefined)
  }

  const cerrarIntento = (
    aprobado: boolean,
    terminado: boolean,
    aciertos?: number,
    errores?: number,
    puntaje?: number,
  ) => {
    const body: Record<string, unknown> = { terminado, aprobado }
    if (aciertos !== undefined) body.aciertos = aciertos
    if (errores !== undefined) body.errores = errores
    if (puntaje !== undefined) body.puntaje = puntaje

    fetch(`/api/study/attempt/${intentoId}/close`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text())
        return res.json() as Promise<CloseResult>
      })
      .then((r) => {
        if (r.warning) {
          setPrecuela(r.precuela)
          setShowWarning(true)
        } else if (!terminado) {
          navigate(-1)
        }
        // si es quiz con resultado, quedarse en la página para ver el resultado
      })
      .catch((err) => setError(err.message))
  }

  // ── Render ───────────────────────────────────────────────

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
        <p>Cargando actividad...</p>
      </div>
    )
  }

  const esQuiz = actividad.tipo === 'quiz' && actividad.preguntas.length > 0
  const respondioTodo =
    !esQuiz || actividad.preguntas.every((p) => respuestas[p.uid] !== undefined)

  return (
    <div style={{ maxWidth: 720, margin: '0 auto', padding: 24 }}>
      <Link to="/">← Volver a Mis cursos</Link>

      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginTop: 16,
          gap: 12,
        }}
      >
        <div>
          <h1 style={{ margin: 0 }}>{actividad.nombre}</h1>
          <span
            style={{
              display: 'inline-block',
              marginTop: 6,
              padding: '2px 10px',
              background: '#e3f2fd',
              color: '#1565c0',
              borderRadius: 12,
              fontSize: 13,
              textTransform: 'capitalize',
            }}
          >
            {actividad.tipo}
          </span>
          <span style={{ marginLeft: 10, fontSize: 13, color: '#666' }}>
            Dificultad: {actividad.dificultad} · Puntaje máx: {actividad.puntaje_maximo}
          </span>
        </div>
        <button
          onClick={handleAbandon}
          style={{ ...btn, background: '#757575', color: 'white', flexShrink: 0 }}
        >
          Abandonar
        </button>
      </div>

      {/* QUIZ */}
      {esQuiz && (
        <div style={{ marginTop: 32 }}>
          {actividad.preguntas.map((preg, qi) => (
            <div
              key={preg.uid}
              style={{
                marginBottom: 28,
                padding: 20,
                border: '1px solid #e0e0e0',
                borderRadius: 10,
                background: '#fafafa',
              }}
            >
              <p style={{ fontWeight: 600, marginTop: 0 }}>
                {qi + 1}. {preg.texto}
                <span style={{ float: 'right', fontSize: 13, color: '#888' }}>
                  {preg.puntaje} pts
                </span>
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {preg.opciones.map((op, idx) => {
                  const seleccionada = respuestas[preg.uid] === idx
                  const correcta = resultado && idx === preg.respuesta_correcta
                  const equivocada =
                    resultado && seleccionada && idx !== preg.respuesta_correcta

                  let bg = seleccionada ? '#bbdefb' : '#fff'
                  let border = seleccionada ? '2px solid #1976d2' : '1px solid #ccc'
                  if (correcta) { bg = '#c8e6c9'; border = '2px solid #388e3c' }
                  if (equivocada) { bg = '#ffcdd2'; border = '2px solid #d32f2f' }

                  return (
                    <button
                      key={idx}
                      onClick={() => handleSelectOpcion(preg.uid, idx)}
                      style={{
                        textAlign: 'left',
                        padding: '10px 14px',
                        background: bg,
                        border,
                        borderRadius: 8,
                        cursor: resultado ? 'default' : 'pointer',
                        fontSize: 14,
                        transition: 'background 0.15s',
                      }}
                    >
                      {String.fromCharCode(65 + idx)}. {op}
                    </button>
                  )
                })}
              </div>
            </div>
          ))}

          {/* Resultado */}
          {resultado && (
            <div
              style={{
                marginTop: 8,
                padding: 20,
                background: resultado.aprobado ? '#e8f5e9' : '#fce4ec',
                borderRadius: 10,
                textAlign: 'center',
              }}
            >
              <h2 style={{ margin: '0 0 8px' }}>
                {resultado.aprobado ? '✅ Aprobado' : '❌ No aprobado'}
              </h2>
              <p style={{ margin: 0 }}>
                Aciertos: {resultado.aciertos} · Errores: {resultado.errores} ·
                Puntaje: {resultado.puntaje} / {actividad.puntaje_maximo}
              </p>
              <button
                onClick={() => navigate(-1)}
                style={{ ...btn, marginTop: 16, background: '#1976d2', color: 'white' }}
              >
                Volver al curso
              </button>
            </div>
          )}

          {!resultado && (
            <button
              onClick={handleSubmitQuiz}
              disabled={!respondioTodo}
              style={{
                ...btn,
                marginTop: 8,
                background: respondioTodo ? '#1976d2' : '#ccc',
                color: 'white',
                width: '100%',
                fontSize: 16,
                padding: '12px 20px',
              }}
            >
              {respondioTodo ? 'Enviar respuestas' : `Respondé todas las preguntas (${Object.keys(respuestas).length}/${actividad.preguntas.length})`}
            </button>
          )}
        </div>
      )}

      {/* EJERCICIO / PROYECTO — auto-evaluación */}
      {!esQuiz && (
        <div
          style={{
            marginTop: 32,
            padding: 28,
            border: '1px solid #e0e0e0',
            borderRadius: 10,
            background: '#fafafa',
            textAlign: 'center',
          }}
        >
          <p style={{ fontSize: 16, color: '#444' }}>
            Completá la {actividad.tipo} de forma autónoma y marcá el resultado.
          </p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 20 }}>
            <button
              onClick={() => handleSelfClose(true)}
              style={{ ...btn, background: '#388e3c', color: 'white', fontSize: 15, padding: '10px 28px' }}
            >
              ✅ Lo completé
            </button>
            <button
              onClick={() => handleSelfClose(false)}
              style={{ ...btn, background: '#d32f2f', color: 'white', fontSize: 15, padding: '10px 28px' }}
            >
              ❌ No pude completarlo
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
            zIndex: 999,
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
            <h2 style={{ marginTop: 0 }}>Te está costando</h2>
            {precuela ? (
              <>
                <p>
                  Considerá repasar primero: <strong>{precuela.nombre}</strong>
                </p>
                <button
                  onClick={() => navigate(-1)}
                  style={{ ...btn, background: '#1976d2', color: 'white' }}
                >
                  Entendido
                </button>
              </>
            ) : (
              <button
                onClick={() => navigate(-1)}
                style={{ ...btn, background: '#1976d2', color: 'white' }}
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
