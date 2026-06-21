import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import cytoscape, { type Core } from 'cytoscape'

interface Nodo {
  id: string
  nombre: string
  descripcion: string
  nivel_dificultad: number
  tiempo_estimado: number
  frecuencia_uso: string
}

interface Arista {
  source: string
  target: string
  tipo: string
  propiedades: Record<string, unknown>
}

interface Estado {
  id: string
  estado: 'no_cursada' | 'aprobada' | 'reprobada' | 'cursando' | 'completada'
}

const ESTADO_COLOR: Record<string, string> = {
  no_cursada: '#1976d2',
  aprobada: '#388e3c',
  reprobada: '#d32f2f',
  cursando: '#7b1fa2',
  completada: '#78909c',
}

const ESTADO_LABEL: Record<string, string> = {
  no_cursada: 'No cursada',
  aprobada: 'Aprobada',
  reprobada: 'Reprobada',
  cursando: 'Cursando',
  completada: 'Completada',
}

const EDGE_COLOR: Record<string, string> = {
  REQUIERE: '#546e7a',
  ALTERNATIVA: '#e65100',
}

export default function SubjectTree() {
  const { id_materia } = useParams<{ id_materia: string }>()
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') ?? '{}')
  const containerRef = useRef<HTMLDivElement>(null)
  const cyRef = useRef<Core | null>(null)
  const nodosRef = useRef<Nodo[]>([])
  const navigateRef = useRef(navigate)
  navigateRef.current = navigate
  const [loading, setLoading] = useState(true)
  const [tooltip, setTooltip] = useState<{ text: string; x: number; y: number } | null>(null)
  const observerRef = useRef<ResizeObserver | null>(null)

  const handleTap = useCallback((evt: cytoscape.EventObject) => {
    const nodeId = evt.target.id()
    const materia = nodosRef.current.find((n) => n.id === nodeId)
    if (materia) navigateRef.current(`/subject/${nodeId}`, { state: materia })
  }, [])

  const handleMouseOver = useCallback((evt: cytoscape.EventObject) => {
    const nodeId = evt.target.id()
    const materia = nodosRef.current.find((n) => n.id === nodeId)
    if (!materia) return
    const pos = evt.renderedPosition
    setTooltip({
      text: `${materia.nombre} · dif ${materia.nivel_dificultad} · ${materia.tiempo_estimado}h`,
      x: pos.x,
      y: pos.y - 20,
    })
  }, [])

  const handleMouseOut = useCallback(() => setTooltip(null), [])

  useEffect(() => {
    fetch(`/api/curriculum/subject/${id_materia}/tree/${user.id}`)
      .then((res) => res.json())
      .then((data: { nodos: Nodo[]; aristas: Arista[]; estados: Estado[] }) => {
        if (!containerRef.current) return

        nodosRef.current = data.nodos
        const estadoById = new Map(data.estados.map((e) => [e.id, e.estado]))

        const nodes = data.nodos.map((n) => ({
          data: { id: n.id, label: n.nombre },
          classes: estadoById.get(n.id) ?? 'no_cursada',
        }))

        const edges = data.aristas.map((a) => ({
          data: {
            id: `${a.source}-${a.target}`,
            source: a.source,
            target: a.target,
            label: a.tipo === 'REQUIERE' ? 'requiere' : 'alternativa',
            tipo: a.tipo,
          },
          classes: a.tipo,
        }))

        const cy = cytoscape({
          container: containerRef.current,
          elements: [...nodes, ...edges],
          style: [
            {
              selector: 'node',
              style: {
                shape: 'round-rectangle',
                label: 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'background-color': ESTADO_COLOR.no_cursada,
                color: '#fff',
                'font-size': 11,
                'font-weight': 'bold',
                width: 130,
                height: 44,
                'text-wrap': 'wrap',
                'text-max-width': '116px',
                'text-events': 'no',
                'border-width': 0,
                padding: '6px',
              },
            },
            ...Object.entries(ESTADO_COLOR).map(([clase, color]) => ({
              selector: `node.${clase}`,
              style: { 'background-color': color },
            })),
            {
              selector: 'edge.REQUIERE',
              style: {
                label: 'data(label)',
                'font-size': 9,
                'text-background-color': '#fff',
                'text-background-opacity': 0.8,
                'text-background-padding': '2px',
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'line-color': EDGE_COLOR.REQUIERE,
                'target-arrow-color': EDGE_COLOR.REQUIERE,
                width: 1.5,
                color: EDGE_COLOR.REQUIERE,
              },
            },
            {
              selector: 'edge.ALTERNATIVA',
              style: {
                label: 'data(label)',
                'font-size': 9,
                'text-background-color': '#fff',
                'text-background-opacity': 0.8,
                'text-background-padding': '2px',
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'line-style': 'dashed',
                'line-color': EDGE_COLOR.ALTERNATIVA,
                'target-arrow-color': EDGE_COLOR.ALTERNATIVA,
                width: 1.5,
                color: EDGE_COLOR.ALTERNATIVA,
              },
            },
          ],
          layout: {
            name: 'breadthfirst',
            directed: true,
            padding: 24,
            spacingFactor: 1.4,
          },
          minZoom: 0.3,
          maxZoom: 2.5,
          wheelSensitivity: 0.3,
        })

        observerRef.current = new ResizeObserver(() => {
          cy.resize()
          cy.fit(undefined, 24)
        })
        observerRef.current.observe(containerRef.current)

        cy.fit(undefined, 24)
        cy.on('tap', 'node', handleTap)
        cy.on('mouseover', 'node', handleMouseOver)
        cy.on('mouseout', 'node', handleMouseOut)

        cyRef.current = cy
        setLoading(false)
      })

    return () => {
      cyRef.current?.destroy()
      observerRef.current?.disconnect()
    }
  }, [user.id, id_materia, handleTap, handleMouseOver, handleMouseOut])

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <div
        style={{
          padding: '10px 20px',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          alignItems: 'center',
          gap: 24,
          flexShrink: 0,
          background: '#fff',
        }}
      >
        <Link to="/tree" style={{ fontWeight: 500 }}>← Volver al árbol</Link>
        <strong style={{ fontSize: 16 }}>Materias relacionadas</strong>
        <span style={{ fontSize: 13, color: '#666' }}>
          Hacé clic en una materia para ver detalles
        </span>
      </div>

      {/* Leyenda */}
      <div
        style={{
          padding: '8px 20px',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          gap: 20,
          flexWrap: 'wrap',
          flexShrink: 0,
          background: '#fafafa',
          fontSize: 12,
        }}
      >
        {Object.entries(ESTADO_LABEL).map(([key, label]) => (
          <span key={key} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span
              style={{
                width: 12,
                height: 12,
                borderRadius: 3,
                background: ESTADO_COLOR[key],
                display: 'inline-block',
                flexShrink: 0,
              }}
            />
            {label}
          </span>
        ))}
        <span style={{ color: '#888', marginLeft: 12 }}>
          <span style={{ borderBottom: '2px solid ' + EDGE_COLOR.REQUIERE, paddingBottom: 1, marginRight: 4 }}>—</span>
          requiere
        </span>
        <span style={{ color: '#888' }}>
          <span style={{ borderBottom: '2px dashed ' + EDGE_COLOR.ALTERNATIVA, paddingBottom: 1, marginRight: 4 }}>--</span>
          alternativa
        </span>
      </div>

      {/* Contenedor del grafo */}
      {loading && (
        <p style={{ padding: 24, color: '#666', flexShrink: 0 }}>Cargando grafo...</p>
      )}
      <div ref={containerRef} style={{ flex: 1, width: '100%', position: 'relative' }}>
        {/* Tooltip */}
        {tooltip && (
          <div
            style={{
              position: 'absolute',
              left: tooltip.x,
              top: tooltip.y,
              transform: 'translate(-50%, -100%)',
              background: 'rgba(0,0,0,0.75)',
              color: '#fff',
              padding: '4px 10px',
              borderRadius: 6,
              fontSize: 12,
              pointerEvents: 'none',
              whiteSpace: 'nowrap',
              zIndex: 10,
            }}
          >
            {tooltip.text}
          </div>
        )}
      </div>
    </div>
  )
}
