import { create } from 'zustand'
import { CrossSectionDefinition } from '../session/base/useCrossSection'
import { CrossSectionStorage } from './CrossSectionLocalStorage'

interface CrossSectionStore {
  sections: CrossSectionDefinition[]
  activeSection: string | null
  currentSessionId: string | null
  
  creationMode: 'none' | 'selecting_points' | 'selecting_holes'
  tempStart: [number, number] | null
  tempStop: [number, number] | null
  tempHoles: string[]
  
  startCreation: () => void
  setTempStart: (point: [number, number]) => void
  setTempStop: (point: [number, number]) => void
  setTempHoles: (holes: string[]) => void
  confirmCreation: (name: string) => void
  cancelCreation: () => void
  
  addSection: (section: Omit<CrossSectionDefinition, 'id'>) => void
  removeSection: (id: string) => void
  setActiveSection: (id: string | null) => void
  toggleVisibility: (id: string) => void
  
  initializeForSession: (sessionId: string) => void
  saveToLocalStorage: () => void
  clearAll: () => void
}

export const useCrossSectionStore = create<CrossSectionStore>((set, get) => ({
  sections: [],
  activeSection: null,
  currentSessionId: null,
  creationMode: 'none',
  tempStart: null,
  tempStop: null,
  tempHoles: [],
  
  startCreation: () => set({ 
    creationMode: 'selecting_points',
    tempStart: null,
    tempStop: null,
    tempHoles: []
  }),
  
  setTempStart: (point) => set({ tempStart: point }),
  
  setTempStop: (point) => set({ 
    tempStop: point,
    creationMode: 'selecting_holes'
  }),
  
  setTempHoles: (holes) => set({ tempHoles: holes }),
  
  confirmCreation: (name) => {
    const { tempStart, tempStop, tempHoles } = get()
    if (!tempStart || !tempStop) return
    
    const section: CrossSectionDefinition = {
      id: `section_${Date.now()}`,
      name,
      xy_start: tempStart,
      xy_stop: tempStop,
      hole_ids: tempHoles,
      tolerance: 100,
      visible: true,
      color: '#ef4444',
    }
    
    set({
      sections: [...get().sections, section],
      activeSection: section.id,
      creationMode: 'none',
      tempStart: null,
      tempStop: null,
      tempHoles: [],
    })
    
    get().saveToLocalStorage()
  },
  
  cancelCreation: () => set({
    creationMode: 'none',
    tempStart: null,
    tempStop: null,
    tempHoles: [],
  }),
  
  addSection: (section) => {
    set((state) => ({
      sections: [...state.sections, { ...section, id: `section_${Date.now()}` }]
    }))
    get().saveToLocalStorage()
  },
  
  removeSection: (id) => {
    set((state) => ({
      sections: state.sections.filter(s => s.id !== id),
      activeSection: state.activeSection === id ? null : state.activeSection,
    }))
    get().saveToLocalStorage()
  },
  
  setActiveSection: (id) => {
    set({ activeSection: id })
    get().saveToLocalStorage()
  },
  
  toggleVisibility: (id) => {
    set((state) => ({
      sections: state.sections.map(s =>
        s.id === id ? { ...s, visible: !s.visible } : s
      )
    }))
    get().saveToLocalStorage()
  },
  
  initializeForSession: (sessionId: string) => {
    console.log('Initializing cross sections for session:', sessionId)
    
    const saved = CrossSectionStorage.load(sessionId)
    
    if (saved) {
      console.log('Restored cross sections:', saved)
      set({
        currentSessionId: sessionId,
        sections: saved.sections,
        activeSection: saved.activeSection,
      })
    } else {
      console.log('Starting fresh for session:', sessionId)
      set({
        currentSessionId: sessionId,
        sections: [],
        activeSection: null,
      })
    }
  },
  
  saveToLocalStorage: () => {
    const { currentSessionId, sections, activeSection } = get()
    if (!currentSessionId) {
      console.warn('⚠️ No session ID, not saving cross sections')
      return
    }
    
    CrossSectionStorage.save(currentSessionId, sections, activeSection)
  },
  
  clearAll: () => {
    set({
      sections: [],
      activeSection: null,
      currentSessionId: null,
      creationMode: 'none',
      tempStart: null,
      tempStop: null,
      tempHoles: [],
    })
    CrossSectionStorage.clear()
  },
}))