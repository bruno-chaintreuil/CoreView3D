import { useState, useEffect } from 'react'
import { Classes } from '@blueprintjs/core'
import '@blueprintjs/core/lib/css/blueprint.css'
import '@blueprintjs/icons/lib/css/blueprint-icons.css'
import axios from 'axios'
import { DrillholeData, parseDrillholeData } from '../../drillholes/base/DrillHole'
import { MainLayout } from './MainLayout'
import { DataLoaderDialog } from '../../drillholes/components/DataLoaderDlg'
import { SessionData, SessionManager } from '../../session/base/SessionManager'
import { SessionRestoreDialog } from '../../session/components/SessionRestore'
import { useViewerStore } from '../base/useViewerStore'

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [drillholeData, setDrillholeData] = useState<DrillholeData | null>(null)
  const [savedSettings, setSavedSettings] = useState<SessionData['settings'] | null>(null)
  const [isLoaderOpen, setIsLoaderOpen] = useState(false)
  const [showSessionRestore, setShowSessionRestore] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const initializeFromSession = useViewerStore(s => s.initializeFromSession)
  const getSessionVisProps = useViewerStore(s => s.getSessionVisProps)

  useEffect(() => {
    const sessionInfo = SessionManager.getSessionInfo()
        
    if (sessionInfo?.sessionId) {
      console.log('Found saved session with ID, showing restore dialog')
      setShowSessionRestore(true)
      const session = SessionManager.loadSession()
      if (session) {
        setSessionId(session.sessionId || null)
        setSavedSettings(session.settings)
      }
    } else {
      console.log('No valid sessionId, clearing old data and opening loader')
      SessionManager.clearSession()
      setIsLoaderOpen(true)
    }
  }, [])

  const loadSessionData = async (sid: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get(`/api/session/load/${sid}`)
   
      if (!response.data.success) {
        throw new Error('Session load failed')
      }

      const parsed = parseDrillholeData({
        trajectories: response.data.data.trajectories,
        assays: response.data.data.assays,
      })

      parsed.sanitizeData()

      setDrillholeData(parsed)
      setSessionId(sid)

      const session = SessionManager.loadSession()
      if (session) {
        initializeFromSession(
          session.settings,
          parsed.trajectories.map(t => t.hole_id)
        )
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error loading session')
      setSessionId(null)
      SessionManager.clearSession()
      setIsLoaderOpen(true)
    } finally {
      setLoading(false)
    }
  }

  const handleDataLoaded = (data: DrillholeData, newSessionId: string) => {
    const holeIds = data.trajectories.map(t => t.hole_id)

    setSessionId(newSessionId)
    setDrillholeData(data)
    
    initializeFromSession(
      {
        visibleHoles: holeIds,
        showCollars: true,
        showLabels: true,
        showEndMarkers: true,
        showGrid: true,
        showBoundingBox: true,
        showAxes: true,
        showDataTree: true,
      },
      holeIds
    )
    
    SessionManager.saveSession(data, getSessionVisProps(), newSessionId)
  }

  const handleRestoreSession = async () => {
    const info = SessionManager.getSessionInfo()
    if (!info?.sessionId) return

    setShowSessionRestore(false)
    await loadSessionData(info.sessionId)
  }

  const handleDismissRestore = () => {
    SessionManager.clearSession()
    setShowSessionRestore(false)
    setSessionId(null)
    setDrillholeData(null)
    setIsLoaderOpen(true)
  }

  const handleOpenLoader = () => {
    setIsLoaderOpen(true)
  }

  const handleSaveSession = (settings: SessionData['settings']) => {
    if (drillholeData && sessionId) {
      SessionManager.saveSession(drillholeData, settings, sessionId)
      setSavedSettings(settings)
    }
  }

  const handleExportSession = (settings: SessionData['settings']) => {
    if (drillholeData) {
      SessionManager.exportSession(drillholeData, settings, sessionId)
    }
  }

  const handleImportSession = async (file: File) => {
    const session = await SessionManager.importSession(file)
    if (session) {
      const parsed = parseDrillholeData(session.data)
      parsed.sanitizeData()
      setDrillholeData(parsed)
      setSessionId(session.sessionId || null)
      initializeFromSession(
        session.settings,
        parsed.trajectories.map(t => t.hole_id)
      )
      SessionManager.saveSession(parsed, session.settings, session.sessionId)
    }
  }

  const handleClearSession = () => {
    SessionManager.clearSession()
    setSessionId(null)
    setDrillholeData(null)
    setIsLoaderOpen(true)
  }

  if (loading) {
    return (
      <div className={Classes.DARK} style={{ 
        height: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: '#293742'
      }}>
        <h2 style={{ color: '#8A9BA8' }}>Loading session...</h2>
      </div>
    )
  }

  if (error) {
    return (
      <div className={Classes.DARK} style={{ 
        height: '100vh', 
        display: 'flex', 
        flexDirection: 'column',
        alignItems: 'center', 
        justifyContent: 'center',
        background: '#293742',
        gap: '16px'
      }}>
        <h2 style={{ color: '#db3737' }}>Error: {error}</h2>
        <button 
          onClick={handleOpenLoader}
          style={{
            padding: '10px 20px',
            background: '#137cbd',
            color: 'white',
            border: 'none',
            borderRadius: '3px',
            cursor: 'pointer'
          }}
        >
          Load New Data
        </button>
      </div>
    )
  }

  return (
    <div className={Classes.DARK} style={{ height: '100vh', overflow: 'hidden' }}>
      {drillholeData && sessionId ? (
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
          <h2 style={{ color: '#8A9BA8' }}>Waiting for data...</h2>
        </div>
      )}

      <SessionRestoreDialog
        isOpen={showSessionRestore}
        sessionInfo={sessionId && savedSettings ? {
          timestamp: new Date().toISOString(),
          holesCount: savedSettings.visibleHoles.length
        } : null}
        onRestore={handleRestoreSession}
        onDismiss={handleDismissRestore}
      />

      <DataLoaderDialog
        isOpen={isLoaderOpen}
        onClose={() => setIsLoaderOpen(false)}
        onDataLoaded={handleDataLoaded}
      />
    </div>
  )
}

export default App