import * as THREE from "three"
import { DrillholeTrajectory, AssayData } from "../../drillholes/base/DrillHole"
import { LITHOLOGY_COLORS, getDefaultDrillholeColor } from "./Geo3DColors"
import { interpolatePointAtDepth, getPointsInInterval } from "./Geo3DInterpolation"
import { Geo3DSpriteObject } from "../base/Geo3DSpriteObject"
import { TextSprite } from "../base/Geo3DTextSprite"

interface Geo3DDrillholeOptions {
  trajectory: DrillholeTrajectory
  assays?: AssayData[]
  showCollar?: boolean
  showEndMarker?: boolean
  showLabel?: boolean
  lineWidth?: number
}

export class Geo3DDrillhole extends Geo3DSpriteObject {
  private trajectory: DrillholeTrajectory
  private assays: AssayData[]
  private options: Required<Geo3DDrillholeOptions>

  constructor(options: Geo3DDrillholeOptions) {
    super()
    const filteredAssays = options.assays?.filter(a => a.Hole_ID === options.trajectory.hole_id) || []
    
    this.trajectory = options.trajectory
    this.assays = this.fillAssayGaps(filteredAssays)

    this.options = {
      ...options,
      showCollar: options.showCollar ?? true,
      showEndMarker: options.showEndMarker ?? true,
      showLabel: options.showLabel ?? true,
      lineWidth: options.lineWidth ?? 3,
      assays: filteredAssays,
    }

    this.build()
  }

  private build() {
    const defaultColor = getDefaultDrillholeColor(this.trajectory.hole_id)

    if (this.assays.length === 0) {
      this.buildSimpleTrajectory(defaultColor)
    } else {
      this.buildColoredTrajectory(defaultColor)
    }

    if (this.options.showCollar) {
      this.addCollarMarker()
    }

    if (this.options.showEndMarker) {
      this.addEndMarker()
    }

    if (this.options.showLabel) {
      this.addLabel()
    }
  }

  private buildSimpleTrajectory(color: number) {
    const points = this.trajectory.points.map(p => new THREE.Vector3(p.x, p.y, p.z))
    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    const material = new THREE.LineBasicMaterial({ color })
    const line = new THREE.Line(geometry, material)
    line.name = `trajectory_${this.trajectory.hole_id}`
    this._object.add(line)
  }

  private fillAssayGaps(assays) {
    if (!assays || assays.length === 0) {
      const maxDepth = Math.max(...this.trajectory.points.map(p => p.depth))
      return [{ Hole_ID: this.trajectory.hole_id, From: 0, To: maxDepth, Lithology: "Unassigned" }]
    }
  
    const maxDepth = Math.max(...this.trajectory.points.map(p => p.depth))
    const sorted = [...assays].sort((a,b)=>a.From-b.From)
    const filled = []
    let lastTo = 0
    for (const a of sorted) {
      if (a.From > lastTo)
        filled.push({ Hole_ID: a.Hole_ID, From: lastTo, To: a.From, Lithology: "Unassigned" })
      filled.push(a)
      lastTo = a.To
    }
    if (lastTo < maxDepth)
      filled.push({ Hole_ID: sorted[0].Hole_ID, From: lastTo, To: maxDepth, Lithology: "Unassigned" })
    return filled
  }  

  private buildColoredTrajectory(defaultColor: number) {
    this.assays.forEach((assay, index) => {
      const color = assay.Lithology 
        ? LITHOLOGY_COLORS[assay.Lithology] ?? defaultColor 
        : defaultColor

      const startPoint = interpolatePointAtDepth(this.trajectory.points, assay.From)
      const endPoint = interpolatePointAtDepth(this.trajectory.points, assay.To)
      
      const segmentPoints = [
        startPoint,
        ...getPointsInInterval(this.trajectory.points, assay.From, assay.To),
        endPoint,
      ]

      const geometry = new THREE.BufferGeometry().setFromPoints(segmentPoints)
      const material = new THREE.LineBasicMaterial({ color })
      const line = new THREE.Line(geometry, material)
      line.name = `segment_${this.trajectory.hole_id}_${index}`
      this._object.add(line)
    })
  }

  private addCollarMarker() {
    const firstPoint = this.trajectory.points[0]
    const geometry = new THREE.SphereGeometry(3, 16, 16)
    const material = new THREE.MeshBasicMaterial({ color: 0xFFD700 })
    const sphere = new THREE.Mesh(geometry, material)
    sphere.position.set(firstPoint.x, firstPoint.y, firstPoint.z)
    sphere.name = `collar_${this.trajectory.hole_id}`
    this._object.add(sphere)
  }

  private addEndMarker() {
      const maxDepth = Math.max(...this.trajectory.points.map(p => p.depth))
      const endPoint = interpolatePointAtDepth(this.trajectory.points, maxDepth)
  
      const geometry = new THREE.SphereGeometry(2, 12, 12)
      const material = new THREE.MeshBasicMaterial({ color: 0xFF0000 })
      const sphere = new THREE.Mesh(geometry, material)
      sphere.position.copy(endPoint)
      sphere.name = `end_${this.trajectory.hole_id}`
  
      this._object.add(sphere)  
  }

  private addLabel() {
    const firstPoint = this.trajectory.points[0]
    const position = new THREE.Vector3(firstPoint.x, firstPoint.y, firstPoint.z)
    position.y += 10
  
    const sprite = new TextSprite({
      text: this.trajectory.hole_id.toString(),
      position,
      color: 0xffffff,
      fontSize: 48,
      bold: true,
      depthTest: false
    })
    
    this._object.add(sprite.object)
  }
 
  getHoleId(): string {
    return this.trajectory.hole_id
  }

  getTrajectory(): DrillholeTrajectory {
    return this.trajectory
  }

  updateAssays(assays: AssayData[]) {
    this.assays = assays.filter(a => a.Hole_ID === this.trajectory.hole_id)
    
    const toRemove: THREE.Object3D[] = []
    this._object.children.forEach(child => {
      if (child.name.startsWith('trajectory_') || child.name.startsWith('segment_')) {
        toRemove.push(child)
      }
    })
    toRemove.forEach(obj => this._object.remove(obj))
    
    const defaultColor = getDefaultDrillholeColor(this.trajectory.hole_id)
    if (this.assays.length === 0) {
      this.buildSimpleTrajectory(defaultColor)
    } else {
      this.buildColoredTrajectory(defaultColor)
    }
  }
}
