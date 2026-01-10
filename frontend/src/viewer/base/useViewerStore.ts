import { create } from 'zustand'

/* ---------- Camera ---------- */

export type CameraView = 'top' | 'front' | 'side' | 'iso' | 'reset'

export interface CameraState {
  position: [number, number, number]
  target: [number, number, number]
}

/* ---------- Store ---------- */

interface ViewerState {
  /* Camera */
  cameraView: CameraView | null
  cameraState: CameraState | null
  setCameraView: (view: CameraView) => void
  setCameraState: (state: CameraState) => void

  /* Z exaggeration */
  zScale: number
  setZScale: (scale: number) => void

  /* Visibility */
  visibleHoles: Set<string>
  toggleHole: (holeId: string) => void
  setVisibleHoles: (holes: Set<string>) => void
  showAllHoles: (holeIds: string[]) => void
  hideAllHoles: () => void

  /* Display options */
  showCollars: boolean
  showLabels: boolean
  showEndMarkers: boolean
  showGrid: boolean
  showBoundingBox: boolean
  showAxes: boolean
  showDataTree: boolean

  setShowCollars: (v: boolean) => void
  setShowLabels: (v: boolean) => void
  setShowEndMarkers: (v: boolean) => void
  setShowGrid: (v: boolean) => void
  setShowBoundingBox: (v: boolean) => void
  setShowAxes: (v: boolean) => void
  setShowDataTree: (v: boolean) => void

  /* Selection */
  selectedHoleId: string | null
  selectedHoleIds: string[]
  setSelectedHoleId: (id: string | null) => void
  toggleSelectedHole: (id: string) => void
  clearSelectedHoles: () => void

  /* Mouse */
  mousePosition: { x: number; y: number; z: number }
  setMousePosition: (p: { x: number; y: number; z: number }) => void

  /* Session */
  initializeFromSession: (settings: any, holeIds: string[]) => void
  getSessionVisProps: () => SessionVisProps
}

const sessionVisSelector = (s: ViewerState) => ({
  visibleHoles: Array.from(s.visibleHoles),
  showCollars: s.showCollars,
  showLabels: s.showLabels,
  showEndMarkers: s.showEndMarkers,
  showGrid: s.showGrid,
  showBoundingBox: s.showBoundingBox,
  showAxes: s.showAxes,
  showDataTree: s.showDataTree,
  camera: s.cameraState,
})

export type SessionVisProps = ReturnType<typeof sessionVisSelector>

/* ---------- Store implementation ---------- */

export const useViewerStore = create<ViewerState>((set, get) => ({
  cameraView: null,
  cameraState: null,
  setCameraView: (view) => set({ cameraView: view }),
  setCameraState: (state) => set({ cameraState: state }),

  zScale: 1.0,
  setZScale: (scale) => set({ zScale: scale }),

  visibleHoles: new Set(),
  toggleHole: (holeId) =>
    set((state) => {
      const s = new Set(state.visibleHoles)
      s.has(holeId) ? s.delete(holeId) : s.add(holeId)
      return { visibleHoles: s }
    }),
  setVisibleHoles: (holes) => set({ visibleHoles: holes }),
  showAllHoles: (holeIds) => set({ visibleHoles: new Set(holeIds) }),
  hideAllHoles: () => set({ visibleHoles: new Set() }),

  showCollars: true,
  showLabels: true,
  showEndMarkers: true,
  showGrid: true,
  showBoundingBox: true,
  showAxes: true,
  showDataTree: true,

  setShowCollars: (v) => set({ showCollars: v }),
  setShowLabels: (v) => set({ showLabels: v }),
  setShowEndMarkers: (v) => set({ showEndMarkers: v }),
  setShowGrid: (v) => set({ showGrid: v }),
  setShowBoundingBox: (v) => set({ showBoundingBox: v }),
  setShowAxes: (v) => set({ showAxes: v }),
  setShowDataTree: (v) => set({ showDataTree: v }),

  selectedHoleId: null,
  selectedHoleIds: [],
  setSelectedHoleId: (id) => set({ selectedHoleId: id }),
  toggleSelectedHole: (id) =>
    set((state) => {
      const s = new Set(state.selectedHoleIds)
      s.has(id) ? s.delete(id) : s.add(id)
      return { selectedHoleIds: Array.from(s) }
    }),
  clearSelectedHoles: () => set({ selectedHoleIds: [] }),

  mousePosition: { x: 0, y: 0, z: 0 },
  setMousePosition: (p) => set({ mousePosition: p }),

  initializeFromSession: (settings, holeIds) =>
    set({
      visibleHoles: new Set(settings?.visibleHoles ?? holeIds),
      showCollars: settings?.showCollars ?? true,
      showLabels: settings?.showLabels ?? true,
      showEndMarkers: settings?.showEndMarkers ?? true,
      showGrid: settings?.showGrid ?? true,
      showBoundingBox: settings?.showBoundingBox ?? true,
      showAxes: settings?.showAxes ?? true,
      showDataTree: settings?.showDataTree ?? true,
      cameraState: settings?.camera ?? null,
      zScale: settings?.zScale ?? 1.0,
    }),

  getSessionVisProps: () => sessionVisSelector(get()),
}))
