import { FC, useEffect, useState } from 'react'
import { DrillholeData } from '../../drillholes/base/DrillHole'
import { MenuBar } from './MenuBar'
import { DataTreePanel } from './DataTreePanel'
import { ViewerCanvas } from './Viewer'
import { SessionData } from '../../session/base/SessionManager'
import { StatusBar } from './StatusBar'
import { useViewerStore } from '../base/useViewerStore'

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
  const vis_store = useViewerStore()
  const vis_props = vis_store.getSessionVisProps()

  useEffect(() => {
    const holeIds = data.trajectories.map(t => t.hole_id)
    vis_store.initializeFromSession(initialSettings, holeIds)
  }, [data, initialSettings])

  useEffect(() => {
    const timeout = setTimeout(() => {
      onSaveSession(vis_props)
    }, 1000)
    return () => clearTimeout(timeout)
  }, [vis_props, onSaveSession])

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
        onSaveSession={() => onSaveSession(vis_props)}
        onExportSession={() => onExportSession(vis_props)}
        onImportSession={onImportSession}
        onClearSession={onClearSession}
      />
        <div style={{ 
          flex: 1, 
          display: 'flex', 
          overflow: 'hidden',
          position: 'relative'
        }}>
          {vis_store.showDataTree && (
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