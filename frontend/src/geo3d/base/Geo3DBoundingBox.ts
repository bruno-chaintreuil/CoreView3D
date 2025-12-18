import * as THREE from "three"
import { Geo3DObject } from "./Geo3DObject"
import { Bounds } from "../../utils/base/Bounds"

interface Geo3DBoundingBoxOptions {
  bounds: Bounds
}

export class Geo3DBoundingBox extends Geo3DObject {
  private bounds: Bounds

  constructor(options: Geo3DBoundingBoxOptions) {
    super()

    this.bounds = options.bounds
    this.build()
  }

  private build() {
    const sizeX = this.bounds.maxX - this.bounds.minX
    const sizeY = this.bounds.maxY - this.bounds.minY
    const sizeZ = this.bounds.maxZ - this.bounds.minZ

    const geometry = new THREE.BoxGeometry(sizeX, sizeY, sizeZ)
    const edges = new THREE.EdgesGeometry(geometry)
    const material = new THREE.LineBasicMaterial({ 
      color: 0x4B5563,
      linewidth: 1 
    })
    const box = new THREE.LineSegments(edges, material)

    box.position.set(
      (this.bounds.maxX + this.bounds.minX) / 2,
      (this.bounds.maxY + this.bounds.minY) / 2,
      (this.bounds.maxZ + this.bounds.minZ) / 2
    )

    box.name = 'boundingBox'
    this._object.add(box)
  }

  getBounds(): Bounds {
    return this.bounds
  }
}
