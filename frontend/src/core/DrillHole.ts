
export interface CollarData {
  Hole_ID: string
  East: number
  North: number
  Elevation: number
  Max_Depth: number
  Azimuth: number
  Dip: number
  Date?: string
  Project?: string
}

export interface SurveyData {
  Hole_ID: string
  Depth: number
  Azimuth: number
  Dip: number
}

export interface AssayData {
  Hole_ID: string
  From: number
  To: number
  Lithology?: string
  [key: string]: string | number | undefined  // Allow dynamic assay columns
}

export interface TrajectoryPoint {
  depth: number
  x: number
  y: number
  z: number
}

export interface DrillholeTrajectory {
  hole_id: string
  collar: {
    east: number
    north: number
    elevation: number
    max_depth: number
    azimuth: number
    dip: number
  }
  points: TrajectoryPoint[]
  has_survey: boolean
}

export interface DrillholeData {
  trajectories: DrillholeTrajectory[]
  assays?: AssayData[]
}

export interface Bounds {
  minX: number
  maxX: number
  minY: number
  maxY: number
  minZ: number
  maxZ: number
}

export function computeBounds(data: DrillholeData): Bounds {
  return data.trajectories.reduce(
    (acc, traj) => {
      traj.points.forEach(p => {
        acc.minX = Math.min(acc.minX, p.x)
        acc.maxX = Math.max(acc.maxX, p.x)
        acc.minY = Math.min(acc.minY, p.y)
        acc.maxY = Math.max(acc.maxY, p.y)
        acc.minZ = Math.min(acc.minZ, p.z)
        acc.maxZ = Math.max(acc.maxZ, p.z)
      })
      return acc
    },
    {
      minX: Infinity,
      maxX: -Infinity,
      minY: Infinity,
      maxY: -Infinity,
      minZ: Infinity,
      maxZ: -Infinity,
    }
  )
}
