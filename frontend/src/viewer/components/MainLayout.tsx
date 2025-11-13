import { FC, useEffect } from 'react'
import { DrillholeData } from '../../drillholes/base/DrillHole'
import { MenuBar } from './MenuBar'
import { DataTreePanel } from './DataTreePanel'
import { ViewerCanvas } from './Viewer'
import { useViewerStore } from '../base/useViewerStore'
import { useSessionData } from '../../session/base/useSession'
import { SessionData } from '../../session/base/SessionManager'
import { StatusBar } from './StatusBar'

interface MainLayoutProps {
  data: DrillholeData
  initialSettings: SessionData['settings'] | null
  onOpenLoader: () => void
  onSaveSession: (settings: SessionData['settings']) => void
  onExportSession: (settings: SessionData['settings']) => void
  onImportSession: (file: File) => void
  onClearSession: () => void
}

export const MainLayout: FC<MainLayoutProps> = ({ 
  data, 
  initialSettings,
  onOpenLoader,
  onSaveSession,
  onExportSession,
  onImportSession,
  onClearSession,
}) => {
  const store = useViewerStore()
  const sessionData = useSessionData()

  useEffect(() => {
    const holeIds = data.trajectories.map(t => t.hole_id)
    store.initializeFromSession(initialSettings, holeIds)
  }, [data, initialSettings])

  useEffect(() => {
    const timeout = setTimeout(() => {
      onSaveSession(sessionData)
    }, 1000)
    return () => clearTimeout(timeout)
  }, [sessionData, onSaveSession])

  const handleExportScreenshot = () => {
    const canvas = document.querySelector('canvas')
    if (!canvas) return

    canvas.toBlob((blob) => {
      if (!blob) return
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      const date = new Date().toISOString().split('T')[0]
      link.href = url
      link.download = `coreview3d_${date}.png`
      link.click()
      URL.revokeObjectURL(url)
    }, 'image/png', 1.0)
  }

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh',
      background: '#293742'
    }}>
      <MenuBar
        onOpenLoader={onOpenLoader}
        onExportScreenshot={handleExportScreenshot}
        onSaveSession={() => onSaveSession(sessionData)}
        onExportSession={() => onExportSession(sessionData)}
        onImportSession={onImportSession}
        onClearSession={onClearSession}
      />
      <div style={{ 
        flex: 1, 
        display: 'flex', 
        overflow: 'hidden',
        position: 'relative'
      }}>
        {store.showDataTree && (
          <DataTreePanel data={data} />
        )}
        <div style={{ flex: 1, position: 'relative' }}>
          <ViewerCanvas data={data} />
        </div>
      </div>
      <StatusBar />
    </div>
  )
}
