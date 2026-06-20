import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
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
  estado: 'no_cursada' | 'aprobada' | 'cursando'
}

const ESTADO_COLOR: Record<string, string> = {
  no_cursada: '#1976d2',
  aprobada: '#388e3c',
  cursando: '#7b1fa2',
}

export default function Tree() {
  const navigate = useNavigate()
  const user = JSON.parse(localStorage.getItem('user') ?? '{}')
  const containerRef = useRef<HTMLDivElement>(null)
  const cyRef = useRef<Core | null>(null)
  const nodosRef = useRef<Nodo[]>([])
  const navigateRef = useRef(navigate)
  navigateRef.current = navigate
  const [loading, setLoading] = useState(true)
  const observerRef = useRef<ResizeObserver | null>(null)

  const handleTap = useCallback((evt: cytoscape.EventObject) => {
    const nodeId = evt.target.id()
    const materia = nodosRef.current.find((n) => n.id === nodeId)
    if (materia) navigateRef.current(`/subject/${nodeId}`, { state: materia })
  }, [])

  useEffect(() => {
    fetch(`/api/curriculum/tree/${user.id}`)
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
            label: a.tipo,
          },
        }))

        const cy = cytoscape({
          container: containerRef.current,
          elements: [...nodes, ...edges],
          style: [
            {
              selector: 'node',
              style: {
                label: 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'background-color': '#1976d2',
                color: '#fff',
                'font-size': 12,
                width: 40,
                height: 40,
                'text-events': 'no',
              },
            },
            ...Object.entries(ESTADO_COLOR).map(([clase, color]) => ({
              selector: `node.${clase}`,
              style: { 'background-color': color },
            })),
            {
              selector: 'edge',
              style: {
                label: 'data(label)',
                'font-size': 10,
                'curve-style': 'bezier',
                'target-arrow-shape': 'triangle',
                'line-color': '#aaa',
                'target-arrow-color': '#aaa',
              },
            },
          ],
        })

        // ResizeObserver mantiene el canvas sincronizado con el contenedor
        observerRef.current = new ResizeObserver(() => {
          cy.resize()
          cy.fit()
        })
        observerRef.current.observe(containerRef.current)

        cy.resize()
        cy.layout({ name: 'breadthfirst', directed: true }).run()

        cy.on('tap', 'node', handleTap)

        cyRef.current = cy
        setLoading(false)
      })

    return () => {
      cyRef.current?.destroy()
      observerRef.current?.disconnect()
    }
  }, [user.id, handleTap])

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '12px 24px', borderBottom: '1px solid #ccc' }}>
        <Link to="/">← Volver</Link>
      </div>
      {loading && <p style={{ padding: 24 }}>Cargando...</p>}
      <div
        ref={containerRef}
        style={{ flex: 1, width: '100%' }}
      />
    </div>
  )
}
