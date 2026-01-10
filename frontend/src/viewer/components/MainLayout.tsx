import { FC, useEffect, useState } from 'react'
import { DrillholeData } from '../../drillholes/base/DrillHole'
import { MenuBar } from './MenuBar'
import { DataTreePanel } from './DataTreePanel'
import { ViewerCanvas } from './Viewer'
import { SessionData } from '../../session/base/SessionManager'
import { StatusBar } from './StatusBar'
import { useViewerStore } from '../base/useViewerStore'
import { CrossSectionCreateDialog } from '../../cross_sections/CrossSectionDlg'
import { CrossSectionViewer } from '../../cross_sections/CrossSectionViewer'
import { HorSplitter } from '../../utils/components/Splitter'
import { useCrossSectionStore } from '../../cross_sections/CrossSectionStore'

interface MainLayoutProps {
  sessionId: string
  data: DrillholeData
  initialSettings: SessionData['settings'] | null
  onOpenLoader: () => void
  onSaveSession: (settings: SessionData['settings']) => void
  onExportSession: (settings: SessionData['settings']) => void
  onImportSession: (file: File) => void
  onClearSession: () => void
}

export const MainLayout: FC<MainLayoutProps> = ({
  sessionId,
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
  const cs_store = useCrossSectionStore()
  const { activeSection, sections } = cs_store
  
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [sectionHeight, setSectionHeight] = useState(300)
  const activeSectionDef = sections.find(s => s.id === activeSection)

  // Initialisations
  useEffect(() => {
    const holeIds = data.trajectories.map(t => t.hole_id)
    vis_store.initializeFromSession(initialSettings, holeIds)
  }, [data, initialSettings])

  useEffect(() => {
    cs_store.initializeForSession(sessionId)
  }, [sessionId])

  // Auto-save debounce
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
      link.download = `coreview3d_${date}.png`
      link.href = url
      link.click()
      URL.revokeObjectURL(url)
    }, 'image/png', 1.0)
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: '#293742',
      overflow: 'hidden'
    }}>
      <MenuBar
        onOpenLoader={onOpenLoader}
        onExportScreenshot={handleExportScreenshot}
        onSaveSession={() => onSaveSession(vis_props)}
        onExportSession={() => onExportSession(vis_props)}
        onImportSession={onImportSession}
        onClearSession={onClearSession}
        onOpenCrossSection={() => setShowCreateDialog(true)}
      />
      <div style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        minHeight: 0,
        overflow: 'hidden'
      }}>        
        {activeSectionDef && (
          <div style={{ flex: '0 0 auto' }}> {/* dummy height */}
            <HorSplitter 
              initHeight={sectionHeight} 
              onHeightChanged={setSectionHeight}
            >
              <CrossSectionViewer
                sessionId={sessionId}
                definition={activeSectionDef}
                onClose={() => cs_store.setActiveSection(null)}
              />
            </HorSplitter>
          </div>
        )}
        <div style={{ 
          flex: 1, 
          display: 'flex',
          minHeight: 0,
          overflow: 'hidden'
        }}>
          {vis_store.showDataTree && <DataTreePanel data={data} />}
          <div style={{ flex: 1, position: 'relative' }}>
            <ViewerCanvas data={data} />
          </div>
        </div>
      </div>
      <StatusBar />
      <CrossSectionCreateDialog
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        data={data}
      />
    </div>
  )  
}