import { CrossSectionDefinition } from "../session/base/useCrossSection"

interface CrossSectionLocalState {
  sessionId: string
  sections: CrossSectionDefinition[]
  activeSection: string | null
  timestamp: string
}

const CROSS_SECTION_KEY = 'coreview3d_cross_sections'

export class CrossSectionStorage {
  static save(
    sessionId: string,
    sections: CrossSectionDefinition[],
    activeSection: string | null
  ): void {
    const state: CrossSectionLocalState = {
      sessionId,
      sections,
      activeSection,
      timestamp: new Date().toISOString()
    }
    
    localStorage.setItem(CROSS_SECTION_KEY, JSON.stringify(state))
    console.log('💾 Saved cross sections to localStorage:', state)
  }

  static load(sessionId: string): {
    sections: CrossSectionDefinition[]
    activeSection: string | null
  } | null {
    const stored = localStorage.getItem(CROSS_SECTION_KEY)
    if (!stored) return null
    
    try {
      const state: CrossSectionLocalState = JSON.parse(stored)
      
      if (state.sessionId !== sessionId) {
        console.log('🔄 Different session, clearing cross sections')
        this.clear()
        return null
      }
      
      console.log('📂 Loaded cross sections from localStorage:', state)
      return {
        sections: state.sections,
        activeSection: state.activeSection
      }
    } catch (e) {
      console.error('Failed to parse cross section data:', e)
      return null
    }
  }

  static clear(): void {
    localStorage.removeItem(CROSS_SECTION_KEY)
    console.log('🗑️ Cleared cross sections from localStorage')
  }


  static getInfo(): { sessionId: string; count: number } | null {
    const stored = localStorage.getItem(CROSS_SECTION_KEY)
    if (!stored) return null
    
    try {
      const state: CrossSectionLocalState = JSON.parse(stored)
      return {
        sessionId: state.sessionId,
        count: state.sections.length
      }
    } catch (e) {
      return null
    }
  }
}