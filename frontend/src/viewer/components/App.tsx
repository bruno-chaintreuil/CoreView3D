import { useState, useEffect } from 'react'
import { Classes } from '@blueprintjs/core'
import '@blueprintjs/core/lib/css/blueprint.css'
import '@blueprintjs/icons/lib/css/blueprint-icons.css'
import { DrillholeData, parseDrillholeData } from '../../drillholes/base/DrillHole'
import { MainLayout } from './MainLayout'
import { DataLoaderDialog } from '../../drillholes/components/DataLoaderDlg'
import { SessionData, SessionManager } from '../../session/base/SessionManager'
import { SessionRestoreDialog } from '../../session/components/SessionRestore'


function App() {
  const [drillholeData, setDrillholeData] = useState<DrillholeData | null>(null)
  const [isLoaderOpen, setIsLoaderOpen] = useState(false)
  const [showSessionRestore, setShowSessionRestore] = useState(false)
  const [sessionToRestore, setSessionToRestore] = useState<SessionData | null>(null)
  const [savedSettings, setSavedSettings] = useState<SessionData['settings'] | null>(null)

  useEffect(() => {
    const sessionInfo = SessionManager.getSessionInfo()
    
    if (sessionInfo) {
      setShowSessionRestore(true)
      const session = SessionManager.loadSession()
      setSessionToRestore(session)
    } else {
      setIsLoaderOpen(true)
    }
  }, [])

  const handleDataLoaded = (data: DrillholeData, autoSave: boolean = true) => {
    setDrillholeData(data)
    
    if (autoSave) {
      const defaultSettings: SessionData['settings'] = {
        visibleHoles: data.trajectories.map(t => t.hole_id),
        showCollars: true,
        showLabels: true,
        showEndMarkers: true,
        showGrid: true,
        showBoundingBox: true,
        showAxes: true,
        showDataTree: true,
      }
      
      SessionManager.saveSession(data, defaultSettings)
    }
  }

  const handleRestoreSession = () => {
    if (sessionToRestore) {
      const parsed = parseDrillholeData(sessionToRestore.data)
      parsed.sanitizeData()
      setDrillholeData(parsed)
      setSavedSettings(sessionToRestore.settings)
      setShowSessionRestore(false)
    }
  }

  const handleDismissRestore = () => {
    setShowSessionRestore(false)
    setIsLoaderOpen(true)
    // Don't clear session yet, user might want to restore later from menu
  }

  const handleOpenLoader = () => {
    setIsLoaderOpen(true)
  }

  const handleSaveSession = (settings: SessionData['settings']) => {
    if (drillholeData) {
      SessionManager.saveSession(drillholeData, settings)
    }
  }

  const handleExportSession = (settings: SessionData['settings']) => {
    if (drillholeData) {
      SessionManager.exportSession(drillholeData, settings)
    }
  }

  const handleImportSession = async (file: File) => {
    const session = await SessionManager.importSession(file)
    if (session) {
      const parsed = parseDrillholeData(session.data)
      parsed.sanitizeData()
      setDrillholeData(parsed)
      setSavedSettings(session.settings)
      SessionManager.saveSession(parsed, session.settings)
    }
  }

  const handleClearSession = () => {
    SessionManager.clearSession()
    setDrillholeData(null)
    setSavedSettings(null)
    setIsLoaderOpen(true)
  }

  return (
    <div className={Classes.DARK} style={{ height: '100vh', overflow: 'hidden' }}>
      {drillholeData ? (
        <MainLayout 
          data={drillholeData}
          initialSettings={savedSettings}
          onOpenLoader={handleOpenLoader}
          onSaveSession={handleSaveSession}
          onExportSession={handleExportSession}
          onImportSession={handleImportSession}
          onClearSession={handleClearSession}
        />
      ) : (
        <div style={{ 
          height: '100vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          background: '#293742'
        }}>
          <h2 style={{ color: '#8A9BA8' }}>Loading...</h2>
        </div>
      )}

      <SessionRestoreDialog
        isOpen={showSessionRestore}
        sessionInfo={sessionToRestore ? {
          timestamp: sessionToRestore.timestamp,
          holesCount: sessionToRestore.data.trajectories.length
        } : null}
        onRestore={handleRestoreSession}
        onDismiss={handleDismissRestore}
      />

      <DataLoaderDialog
        isOpen={isLoaderOpen}
        onClose={() => setIsLoaderOpen(false)}
        onDataLoaded={(data) => handleDataLoaded(data, true)}
      />
    </div>
  )
}

export default App