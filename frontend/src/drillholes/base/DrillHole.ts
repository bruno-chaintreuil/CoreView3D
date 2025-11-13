import { BoundData } from "../../utils/Bounds"
import { TrajectoryPoint } from "../../utils/Trajectory"

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
  [key: string]: string | number | undefined
}

export class DrillholeTrajectory extends BoundData {
  hole_id: string
  collar: {
    east: number
    north: number
    elevation: number
    max_depth: number
    azimuth: number
    dip: number
  }
  has_survey: boolean

  constructor(
    hole_id: string,
    collar: CollarData,
    points: TrajectoryPoint[] = [],
    has_survey: boolean = false
  ) {
    super(points)
    this.hole_id = hole_id
    this.collar = {
      east: collar.East,
      north: collar.North,
      elevation: collar.Elevation,
      max_depth: collar.Max_Depth,
      azimuth: collar.Azimuth,
      dip: collar.Dip,
    }
    this.has_survey = has_survey
  }

  sanitizePoints() {
    const cleaned: TrajectoryPoint[] = []
    for (const p of this.points) {
      const prev = cleaned[cleaned.length - 1]
      if (!prev || p.depth !== prev.depth) cleaned.push(p)
    }
    this.points = cleaned
  }
}

export class DrillholeData extends BoundData {
  trajectories: DrillholeTrajectory[]
  assays: AssayData[]

  constructor(trajectories: DrillholeTrajectory[] = [], assays: AssayData[] = []) {
    const allPoints = trajectories.flatMap(t => t.points)
    super(allPoints)
    this.trajectories = trajectories
    this.assays = assays
  }

  sanitizeData() {
    this.trajectories.forEach(t => t.sanitizePoints())

    const maxDepthAll = Math.max(...this.trajectories.map(t => t.collar.max_depth))
    this.assays = this.assays.map(a => ({
      ...a,
      From: Math.max(0, Math.min(a.From, maxDepthAll)),
      To: Math.max(0, Math.min(a.To, maxDepthAll)),
    }))

    this.points = this.trajectories.flatMap(t => t.points)
  }
}

// helper to convert JSON to class instances
export function parseDrillholeData(json: any): DrillholeData {
  const trajectories = json.trajectories.map((t: any) => 
    new DrillholeTrajectory(
      t.hole_id,
      {
        Hole_ID: t.hole_id,
        East: t.collar.east,
        North: t.collar.north,
        Elevation: t.collar.elevation,
        Max_Depth: t.collar.max_depth,
        Azimuth: t.collar.azimuth,
        Dip: t.collar.dip,
      },
      t.points as TrajectoryPoint[],
      t.has_survey
    )
  )
  const assays = json.assays || []
  return new DrillholeData(trajectories, assays)
}
