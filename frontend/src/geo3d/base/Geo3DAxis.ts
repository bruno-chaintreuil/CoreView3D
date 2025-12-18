import * as THREE from "three"
import { Geo3DSpriteObject } from "./Geo3DSpriteObject"
import { TextSprite } from "./Geo3DTextSprite"
import { Bounds } from "../../utils/base/Bounds"

export interface Geo3DAxesOptions {
  bounds: Bounds
  realBounds: Bounds
  axisLength?: number
  showTicks?: boolean
  tickInterval?: number
  tickSize?: number
  colors?: { x: number; y: number; z: number }
}

export class Geo3DAxes extends Geo3DSpriteObject {
  private options: Required<Geo3DAxesOptions>
  private bounds: Bounds
  private realBounds: Bounds
  private spriteList: THREE.Sprite[] = []

  constructor(options: Geo3DAxesOptions) {
    super()
    this.bounds = options.bounds
    this.realBounds = options.realBounds
    this.options = {
      bounds: options.bounds,
      realBounds: options.realBounds,
      axisLength: options.axisLength ?? 30,
      showTicks: options.showTicks ?? true,
      tickInterval: options.tickInterval ?? 50,
      tickSize: options.tickSize ?? 4,
      colors: options.colors ?? { x: 0xef4444, y: 0x10b981, z: 0x3b82f6 },
    }
    this.build()
  }

  private build() {
    this.createAxis("x", "E", new THREE.Vector3(1, 0, 0))
    this.createAxis("y", "N", new THREE.Vector3(0, 1, 0))
    this.createAxis("z", "Z", new THREE.Vector3(0, 0, 1))
    if (this.options.showTicks) this.createTicks()
  }

  private createAxis(axis: "x" | "y" | "z", label: string, direction: THREE.Vector3) {
    const { bounds, options } = this
    const { axisLength, colors } = options

    let start: THREE.Vector3, end: THREE.Vector3, arrowPos: THREE.Vector3, labelPos: THREE.Vector3, color: number

    if (axis === "x") {
      start = new THREE.Vector3(bounds.minX, bounds.minY, bounds.minZ)
      end = new THREE.Vector3(bounds.maxX + axisLength, bounds.minY, bounds.minZ)
      arrowPos = new THREE.Vector3(bounds.maxX + axisLength - 10, bounds.minY, bounds.minZ)
      labelPos = new THREE.Vector3(bounds.maxX + axisLength + 10, bounds.minY, bounds.minZ)
      color = colors.x
    } else if (axis === "y") {
      start = new THREE.Vector3(bounds.minX, bounds.minY, bounds.minZ)
      end = new THREE.Vector3(bounds.minX, bounds.maxY + axisLength, bounds.minZ)
      arrowPos = new THREE.Vector3(bounds.minX, bounds.maxY + axisLength - 10, bounds.minZ)
      labelPos = new THREE.Vector3(bounds.minX, bounds.maxY + axisLength + 10, bounds.minZ)
      color = colors.y
    } else {
      start = new THREE.Vector3(bounds.minX, bounds.minY, bounds.minZ)
      end = new THREE.Vector3(bounds.minX, bounds.minY, bounds.maxZ + axisLength)
      arrowPos = new THREE.Vector3(bounds.minX, bounds.minY, bounds.maxZ + axisLength - 10)
      labelPos = new THREE.Vector3(bounds.minX, bounds.minY, bounds.maxZ + axisLength + 10)
      color = colors.z
    }

    const geometry = new THREE.BufferGeometry().setFromPoints([start, end])
    const material = new THREE.LineBasicMaterial({ color })
    const line = new THREE.Line(geometry, material)
    this._object.add(line)

    const arrowHelper = new THREE.ArrowHelper(direction, arrowPos, 10, color, 4, 3)
    this._object.add(arrowHelper)

    this.addTextSprite(label, labelPos, color, 1)
  }

  private createTicks() {
    this.createAxisTicks("x")
    this.createAxisTicks("y")
    this.createAxisTicks("z")
  }

  private createAxisTicks(axis: "x" | "y" | "z") {
    const { bounds, realBounds, options } = this
    const { tickInterval, tickSize } = options

    let min: number, max: number, realMin: number
    let getTickPosition: (v: number) => THREE.Vector3
    let getTickEnd: (p: THREE.Vector3) => THREE.Vector3
    let getLabelPosition: (p: THREE.Vector3) => THREE.Vector3

    if (axis === "x") {
      min = bounds.minX
      max = bounds.maxX
      realMin = realBounds.minX
      getTickPosition = (v) => new THREE.Vector3(v, bounds.minY, bounds.minZ)
      getTickEnd = (p) => new THREE.Vector3(p.x, p.y, p.z - tickSize)
      getLabelPosition = (p) => new THREE.Vector3(p.x, p.y - tickSize, p.z - tickSize)
    } else if (axis === "y") {
      min = bounds.minY
      max = bounds.maxY
      realMin = realBounds.minY
      getTickPosition = (v) => new THREE.Vector3(bounds.minX, v, bounds.minZ)
      getTickEnd = (p) => new THREE.Vector3(p.x, p.y, p.z - tickSize)
      getLabelPosition = (p) => new THREE.Vector3(p.x - tickSize, p.y, p.z - tickSize)
    } else {
      min = bounds.minZ
      max = bounds.maxZ
      realMin = realBounds.minZ
      getTickPosition = (v) => new THREE.Vector3(bounds.minX, bounds.minY, v)
      getTickEnd = (p) => new THREE.Vector3(p.x - tickSize, p.y, p.z)
      getLabelPosition = (p) => new THREE.Vector3(p.x - tickSize, p.y - tickSize, p.z)
    }

    const range = max - min
    const numTicks = Math.ceil(range / tickInterval)

    for (let idx = 0; idx <= numTicks; idx++) {
      const localValue = min + idx * tickInterval
      if (localValue > max) break
      const realValue = realMin + idx * tickInterval
      const tickPos = getTickPosition(localValue)
      const tickEnd = getTickEnd(tickPos)

      const geometry = new THREE.BufferGeometry().setFromPoints([tickPos, tickEnd])
      const material = new THREE.LineBasicMaterial({ color: 0x888888 })
      const tick = new THREE.Line(geometry, material)
      this._object.add(tick)

      const labelPos = getLabelPosition(tickPos)
      this.addTextSprite(realValue.toFixed(0), labelPos, 0xffffff, 30 )
    }
  }

  private addTextSprite(text: string, position: THREE.Vector3, color: number, fontSize: number, bold = false) {
    const sprite = new TextSprite({
      text,
      position,
      color,
      fontSize,
      bold,
      depthTest: true
    })
    
    this.spriteList.push(sprite.object)
    this._object.add(sprite.object)
  }
}