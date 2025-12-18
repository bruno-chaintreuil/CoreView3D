import { TrajectoryPoint } from "./Trajectory"

export class BoundData {
    points: TrajectoryPoint[]
  
    constructor(points: TrajectoryPoint[] = []) {
      this.points = points
    }
  
    computeBounds(): Bounds {
      const bounds: Bounds = {
        minX: Infinity,
        maxX: -Infinity,
        minY: Infinity,
        maxY: -Infinity,
        minZ: Infinity,
        maxZ: -Infinity,
      }
  
      for (const p of this.points) {
        bounds.minX = Math.min(bounds.minX, p.x)
        bounds.maxX = Math.max(bounds.maxX, p.x)
        bounds.minY = Math.min(bounds.minY, p.y)
        bounds.maxY = Math.max(bounds.maxY, p.y)
        bounds.minZ = Math.min(bounds.minZ, p.z)
        bounds.maxZ = Math.max(bounds.maxZ, p.z)
      }
  
      return bounds
    }
  }
  
  export interface Bounds {
    minX: number
    maxX: number
    minY: number
    maxY: number
    minZ: number
    maxZ: number
  }