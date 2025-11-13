import { useViewerStore } from "../../viewer/base/useViewerStore"

export const useSessionData = () => {
    const store = useViewerStore()
    
    return {
      visibleHoles: Array.from(store.visibleHoles),
      showCollars: store.showCollars,
      showLabels: store.showLabels,
      showEndMarkers: store.showEndMarkers,
      showGrid: store.showGrid,
      showBoundingBox: store.showBoundingBox,
      showAxes: store.showAxes,
      showDataTree: store.showDataTree,
      camera: store.cameraState,
    }
  }