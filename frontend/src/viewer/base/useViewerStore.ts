import { create } from 'zustand'

export type CameraView = 'top' | 'front' | 'side' | 'iso' | 'reset'

interface CameraState {
  position: [number, number, number]
  target: [number, number, number]
}

interface ViewerState {
  // Camera
  cameraView: CameraView | null
  cameraState: CameraState | null
  setCameraView: (view: CameraView) => void
  setCameraState: (state: CameraState) => void
  
  // Visibility
  visibleHoles: Set<string>
  toggleHole: (holeId: string) => void
  setVisibleHoles: (holes: Set<string>) => void
  showAllHoles: () => void
  hideAllHoles: () => void
  
  // Display options
  showCollars: boolean
  showLabels: boolean
  showEndMarkers: boolean
  showGrid: boolean
  showBoundingBox: boolean
  showAxes: boolean
  showDataTree: boolean
  
  setShowCollars: (show: boolean) => void
  setShowLabels: (show: boolean) => void
  setShowEndMarkers: (show: boolean) => void
  setShowGrid: (show: boolean) => void
  setShowBoundingBox: (show: boolean) => void
  setShowAxes: (show: boolean) => void
  setShowDataTree: (show: boolean) => void
  
  // Selection
  selectedHoleId: string | null
  setSelectedHoleId: (id: string | null) => void
  
  // Mouse position
  mousePosition: { x: number; y: number; z: number }
  setMousePosition: (pos: { x: number; y: number; z: number }) => void
  
  // Initialize from session
  initializeFromSession: (settings: any, holeIds: string[]) => void
}

export const useViewerStore = create<ViewerState>((set, get) => ({
  // Camera initial state
  cameraView: null,
  cameraState: null,
  setCameraView: (view) => set({ cameraView: view }),
  setCameraState: (state) => set({ cameraState: state }),
  
  // Visibility initial state
  visibleHoles: new Set<string>(),
  toggleHole: (holeId) => set((state) => {
    const newSet = new Set(state.visibleHoles)
    if (newSet.has(holeId)) {
      newSet.delete(holeId)
    } else {
      newSet.add(holeId)
    }
    return { visibleHoles: newSet }
  }),
  setVisibleHoles: (holes) => set({ visibleHoles: holes }),
  showAllHoles: () => {
    // This will be called with all hole IDs from the component
    // We need the hole IDs to be passed, so we'll handle this differently
  },
  hideAllHoles: () => set({ visibleHoles: new Set() }),
  
  // Display options initial state
  showCollars: true,
  showLabels: true,
  showEndMarkers: true,
  showGrid: true,
  showBoundingBox: true,
  showAxes: true,
  showDataTree: true,
  
  setShowCollars: (show) => set({ showCollars: show }),
  setShowLabels: (show) => set({ showLabels: show }),
  setShowEndMarkers: (show) => set({ showEndMarkers: show }),
  setShowGrid: (show) => set({ showGrid: show }),
  setShowBoundingBox: (show) => set({ showBoundingBox: show }),
  setShowAxes: (show) => set({ showAxes: show }),
  setShowDataTree: (show) => set({ showDataTree: show }),
  
  // Selection
  selectedHoleId: null,
  setSelectedHoleId: (id) => set({ selectedHoleId: id }),
  
  // Mouse position
  mousePosition: { x: 0, y: 0, z: 0 },
  setMousePosition: (pos) => set({ mousePosition: pos }),
  
  // Initialize from session
  initializeFromSession: (settings, holeIds) => {
    set({
      visibleHoles: new Set(settings?.visibleHoles || holeIds),
      showCollars: settings?.showCollars ?? true,
      showLabels: settings?.showLabels ?? true,
      showEndMarkers: settings?.showEndMarkers ?? true,
      showGrid: settings?.showGrid ?? true,
      showBoundingBox: settings?.showBoundingBox ?? true,
      showAxes: settings?.showAxes ?? true,
      showDataTree: settings?.showDataTree ?? true,
      cameraState: settings?.camera || null,
    })
  },
}))