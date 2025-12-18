
import * as THREE from "three"
import { Geo3DObject } from "./Geo3DObject"
import { Bounds } from "../../utils/base/Bounds"

interface Geo3DGridOptions {
  bounds: Bounds
  cellSize?: number
  subdivisions?: number
  color?: number
  opacity?: number
}

export class Geo3DGrid extends Geo3DObject {
  private options: Required<Geo3DGridOptions>

  constructor(options: Geo3DGridOptions) {
    super()
    
    this.options = {
      bounds: options.bounds, 
      cellSize: options.cellSize ?? 20,
      subdivisions: options.subdivisions ?? 10,
      color: options.color ?? 0x444444,
      opacity: options.opacity ?? 0.3,
    }

    this.build()
  }

  private build() {
    const { bounds, cellSize, color, opacity } = this.options
  
    const sizeX = bounds.maxX - bounds.minX
    const sizeY = bounds.maxY - bounds.minY
    const divisionsX = Math.floor(sizeX / cellSize)
    const divisionsY = Math.floor(sizeY / cellSize)
    const z = bounds.minZ
  
    const material = new THREE.LineBasicMaterial({
      color,
      transparent: true,
      opacity,
    })
  
    const grid = new THREE.Group()
  
    for (let i = 0; i <= divisionsX; i++) {
      const x = bounds.minX + i * cellSize
      if (x > bounds.maxX) break
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(x, bounds.minY, z),
        new THREE.Vector3(x, bounds.maxY, z),
      ])
      grid.add(new THREE.Line(geometry, material))
    }
  
    for (let j = 0; j <= divisionsY; j++) {
      const y = bounds.minY + j * cellSize
      if (y > bounds.maxY) break
      const geometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(bounds.minX, y, z),
        new THREE.Vector3(bounds.maxX, y, z),
      ])
      grid.add(new THREE.Line(geometry, material))
    }
  
    this._object.add(grid)
  }  
 
}