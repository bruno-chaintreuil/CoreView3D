import { DrillholeData } from '../../drillholes/base/DrillHole'

export interface SessionData {
  timestamp: string
  sessionId?: string
  data: {
    trajectories: any[]
    assays?: any[]
  }
  settings: {
    visibleHoles: string[]
    showCollars: boolean
    showLabels: boolean
    showEndMarkers: boolean
    showGrid: boolean
    showBoundingBox: boolean
    showAxes: boolean
    showDataTree: boolean
  }
}

const SESSION_KEY = 'coreview3d_session'

export class SessionManager {
  static saveSession(
    data: DrillholeData, 
    settings: SessionData['settings'],
    sessionId?: string
  ): void {
    const session: SessionData = {
      timestamp: new Date().toISOString(),
      sessionId,
      data: {
        trajectories: data.trajectories,
        assays: data.assays
      },
      settings
    }
    
    localStorage.setItem(SESSION_KEY, JSON.stringify(session))
  }

  static loadSession(): SessionData | null {
    const stored = localStorage.getItem(SESSION_KEY)
    if (!stored) return null
    
    try {
      return JSON.parse(stored) as SessionData
    } catch (e) {
      console.error('Failed to parse session data:', e)
      return null
    }
  }

  static getSessionInfo(): { timestamp: string; holesCount: number; sessionId?: string } | null {
    const session = this.loadSession()
    if (!session) return null
    
    return {
      timestamp: session.timestamp,
      holesCount: session.data.trajectories.length,
      sessionId: session.sessionId
    }
  }

  static clearSession(): void {
    localStorage.removeItem(SESSION_KEY)
  }

  static exportSession(
    data: DrillholeData, 
    settings: SessionData['settings'],
    sessionId?: string
  ): void {
    const session: SessionData = {
      timestamp: new Date().toISOString(),
      sessionId,
      data: {
        trajectories: data.trajectories,
        assays: data.assays
      },
      settings
    }
    
    const blob = new Blob([JSON.stringify(session, null, 2)], { 
      type: 'application/json' 
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    const date = new Date().toISOString().split('T')[0]
    link.href = url
    link.download = `coreview3d_session_${date}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  static async importSession(file: File): Promise<SessionData | null> {
    try {
      const text = await file.text()
      const session = JSON.parse(text) as SessionData
      
      // Validate session structure
      if (!session.data || !session.data.trajectories) {
        throw new Error('Invalid session file format')
      }
      
      return session
    } catch (e) {
      console.error('Failed to import session:', e)
      return null
    }
  }
}