import { create } from 'zustand'

export interface CrossSectionDefinition {
  id: string
  name: string
  xy_start: [number, number]
  xy_stop: [number, number]
  hole_ids: string[]
  tolerance: number
  visible: boolean
  color: string
}

export interface ProjectedDrillhole {
  hole_id: string
  trace: Array<{
    x: number
    z: number
  }>
}

export interface CrossSectionData {
  xy_start: [number, number]
  xy_stop: [number, number]
  length: number
  drillholes: ProjectedDrillhole[]
}
