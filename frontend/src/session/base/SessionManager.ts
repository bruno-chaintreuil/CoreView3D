import { DrillholeData } from '../../drillholes/base/DrillHole'

export interface SessionData {
  version: string
  timestamp: string
  data: DrillholeData
  settings: {
    visibleHoles: string[]
    showCollars: boolean
    showLabels: boolean
    showEndMarkers: boolean
    showGrid: boolean
    showBoundingBox: boolean
    showAxes: boolean
    showDataTree: boolean
    camera?: {
      position: [number, number, number]
      target: [number, number, number]
    }
  }
}

const SESSION_KEY = 'coreview3d_session'
const SESSION_VERSION = '1.0.0'

export class SessionManager {
  static saveSession(data: DrillholeData, settings: SessionData['settings']): boolean {
    try {
      const session: SessionData = {
        version: SESSION_VERSION,
        timestamp: new Date().toISOString(),
        data,
        settings,
      }

      const serialized = JSON.stringify(session)
      localStorage.setItem(SESSION_KEY, serialized)
      
      console.log('✓ Session saved', {
        holes: data.trajectories.length,
        assays: data.assays?.length || 0,
        size: `${(serialized.length / 1024).toFixed(2)} KB`
      })
      
      return true
    } catch (error) {
      console.error('Failed to save session:', error)
      return false
    }
  }

  static loadSession(): SessionData | null {
    try {
      const serialized = localStorage.getItem(SESSION_KEY)
      if (!serialized) {
        return null
      }

      const session: SessionData = JSON.parse(serialized)
      
      if (session.version !== SESSION_VERSION) {
        console.warn('Session version mismatch, clearing old session')
        this.clearSession()
        return null
      }

      console.log('✓ Session loaded', {
        timestamp: session.timestamp,
        holes: session.data.trajectories.length,
        assays: session.data.assays?.length || 0,
      })

      return session
    } catch (error) {
      console.error('Failed to load session:', error)
      this.clearSession()
      return null
    }
  }

  static clearSession(): void {
    localStorage.removeItem(SESSION_KEY)
    console.log('✓ Session cleared')
  }

  static hasSession(): boolean {
    return localStorage.getItem(SESSION_KEY) !== null
  }

  static exportSession(data: DrillholeData, settings: SessionData['settings']): void {
    const session: SessionData = {
      version: SESSION_VERSION,
      timestamp: new Date().toISOString(),
      data,
      settings,
    }

    const json = JSON.stringify(session, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    
    const link = document.createElement('a')
    const timestamp = new Date().toISOString().split('T')[0]
    link.href = url
    link.download = `coreview3d_session_${timestamp}.json`
    link.click()
    
    URL.revokeObjectURL(url)
    console.log('✓ Session exported')
  }

  static async importSession(file: File): Promise<SessionData | null> {
    try {
      const text = await file.text()
      const session: SessionData = JSON.parse(text)

      if (!session.data || !session.data.trajectories) {
        throw new Error('Invalid session file structure')
      }

      console.log('✓ Session imported', {
        timestamp: session.timestamp,
        holes: session.data.trajectories.length,
      })

      return session
    } catch (error) {
      console.error('Failed to import session:', error)
      return null
    }
  }

  static getSessionInfo(): { timestamp: string; holesCount: number } | null {
    try {
      const serialized = localStorage.getItem(SESSION_KEY)
      if (!serialized) return null

      const session: SessionData = JSON.parse(serialized)
      return {
        timestamp: session.timestamp,
        holesCount: session.data.trajectories.length,
      }
    } catch {
      return null
    }
  }
}