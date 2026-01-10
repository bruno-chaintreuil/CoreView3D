import { Card, Classes, Spinner, Button, Tag } from '@blueprintjs/core'
import { FC, useRef, useState, useEffect, RefObject } from 'react'
import { CrossSectionDefinition } from '../session/base/useCrossSection'
import { useCrossSectionData } from './useCrossSectionData'
import { CrossSectionChart } from './CrossSectionChart'

interface StatusViewProps {
  loading?: boolean
  error?: string | null
  message?: string
  onRetry?: () => void
}

export const StatusView = ({ loading, error, message, onRetry }: StatusViewProps) => (
  <Card className={Classes.DARK} style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 0 }}>
    <div style={{ textAlign: 'center', maxWidth: 400 }}>
      {loading && <Spinner size={50} />}
      {error && (
        <>
          <div style={{ color: '#ef4444', marginBottom: 8 }}>Error</div>
          <div style={{ color: '#fca5a5', marginBottom: 16 }}>{error}</div>
          {onRetry && <Button intent="danger" onClick={onRetry}>Retry</Button>}
        </>
      )}
      {!loading && !error && <div style={{ color: '#8A9BA8' }}>{message}</div>}
      {loading && message && <div style={{ marginTop: 16, color: '#8A9BA8' }}>{message}</div>}
    </div>
  </Card>
)


export const useResizeObserver = (ref: RefObject<HTMLElement>) => {
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })

  useEffect(() => {
    const element = ref.current
    if (!element) return

    const observer = new ResizeObserver((entries) => {
      if (!entries || entries.length === 0) return
      const { width, height } = entries[0].contentRect
      setDimensions({ width, height })
    })

    observer.observe(element)

    return () => {
      observer.disconnect()
    }
  }, [ref])

  return dimensions
}

interface CrossSectionViewerProps {
  sessionId: string
  definition: CrossSectionDefinition
  onClose: () => void
}

interface CrossSectionViewerProps {
  sessionId: string
  definition: CrossSectionDefinition
  onClose: () => void
}

export const CrossSectionViewer: FC<CrossSectionViewerProps> = ({ sessionId, definition, onClose }) => {
  const { data, loading, error, refetch } = useCrossSectionData(sessionId, definition)
  
  const containerRef = useRef<HTMLDivElement>(null)
  const { width, height } = useResizeObserver(containerRef)

  return (
    <div style={{ 
      height: '100%', 
      width: '100%', 
      display: 'flex', 
      flexDirection: 'column', 
      background: '#1C2127', 
      overflow: 'hidden' 
    }}>
      <div style={{ 
        padding: '12px', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        background: '#293742', 
        borderBottom: '1px solid #394b59',
        flexShrink: 0 
      }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <h6 className={Classes.HEADING} style={{ margin: 0 }}>{definition.name}</h6>
          {data?.length != null && <Tag minimal>{data.length.toFixed(0)}m</Tag>}
          {data?.drillholes && <Tag minimal>{data.drillholes.length} holes</Tag>}
        </div>
        <Button icon="cross" minimal onClick={onClose} />
      </div>
      <div 
        ref={containerRef} 
        style={{ 
          flex: 1,
          minHeight: 0,
          position: 'relative',
          overflow: 'hidden' 
        }}
      >
        {loading && <StatusView loading message="Calculating cross section..." />}
        {error && <StatusView error={error} onRetry={refetch} />}
        {!loading && !error && !data && <StatusView message="No data available" />}
        {!loading && data && width > 0 && height > 0 && (
          <CrossSectionChart 
            data={data} 
            width={width} 
            height={height} 
          />
        )}
      </div>
    </div>
  )
}