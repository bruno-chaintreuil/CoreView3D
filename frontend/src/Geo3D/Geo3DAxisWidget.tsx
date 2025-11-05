// Geo3D/objects/Geo3DAxes.ts
import * as THREE from "three"
import { Geo3DObject } from "./Geo3DObject"
import { Bounds } from "../core/DrillHole"

interface Geo3DAxesOptions {
  bounds: Bounds
  realBounds: Bounds
  axisLength?: number
  showTicks?: boolean
  tickInterval?: number
  colors?: {
    x: number
    y: number
    z: number
  }
}

export class Geo3DAxes extends Geo3DObject {
  private options: Required<Geo3DAxesOptions>
  private bounds: Bounds
  private realBounds: Bounds

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
      colors: options.colors ?? {
        x: 0xEF4444,
        y: 0x10B981,
        z: 0x3B82F6,
      }
    }

    this.build()
  }

  private build() {
    this.createXAxis()
    this.createYAxis()
    this.createZAxis()
    
    if (this.options.showTicks) {
      this.createTicks()
    }
  }

  private createXAxis() {
    const { minX, maxX, minY, minZ } = this.bounds
    const { axisLength, colors } = this.options

    const points = [
      new THREE.Vector3(minX, minY, minZ),
      new THREE.Vector3(maxX + axisLength, minY, minZ)
    ]
    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    const material = new THREE.LineBasicMaterial({ color: colors.x })
    const line = new THREE.Line(geometry, material)
    line.name = 'axis_x'
    this._object.add(line)

    const arrowHelper = new THREE.ArrowHelper(
      new THREE.Vector3(1, 0, 0),
      new THREE.Vector3(maxX + axisLength - 10, minY, minZ),
      10,
      colors.x,
      4,
      3
    )
    this._object.add(arrowHelper)
    this.createTextSprite('E', new THREE.Vector3(maxX + axisLength + 10, minY, minZ), colors.x)
  }

  private createYAxis() {
    const { minX, minY, maxY, minZ } = this.bounds
    const { axisLength, colors } = this.options

    const points = [
      new THREE.Vector3(minX, minY, minZ),
      new THREE.Vector3(minX, maxY + axisLength, minZ)
    ]
    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    const material = new THREE.LineBasicMaterial({ color: colors.y })
    const line = new THREE.Line(geometry, material)
    line.name = 'axis_y'
    this._object.add(line)

    const arrowHelper = new THREE.ArrowHelper(
      new THREE.Vector3(0, 1, 0),
      new THREE.Vector3(minX, maxY + axisLength - 10, minZ),
      10,
      colors.y,
      4,
      3
    )
    this._object.add(arrowHelper)
    this.createTextSprite('N', new THREE.Vector3(minX, maxY + axisLength + 10, minZ), colors.y)
  }

  private createZAxis() {
    const { minX, minY, minZ, maxZ } = this.bounds
    const { axisLength, colors } = this.options

    const points = [
      new THREE.Vector3(minX, minY, minZ),
      new THREE.Vector3(minX, minY, maxZ + axisLength)
    ]
    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    const material = new THREE.LineBasicMaterial({ color: colors.z })
    const line = new THREE.Line(geometry, material)
    line.name = 'axis_z'
    this._object.add(line)

    const arrowHelper = new THREE.ArrowHelper(
      new THREE.Vector3(0, 0, 1),
      new THREE.Vector3(minX, minY, maxZ + axisLength - 10),
      10,
      colors.z,
      4,
      3
    )
    this._object.add(arrowHelper)
    this.createTextSprite('Z', new THREE.Vector3(minX, minY, maxZ + axisLength + 10), colors.z)
  }

  private createTicks() {
    this.createAxisTicks('x')
    this.createAxisTicks('y')
    this.createAxisTicks('z')
  }

  private createAxisTicks(axis: 'x' | 'y' | 'z') {
    const { bounds, realBounds, options } = this
    const { tickInterval } = options

    let min: number, max: number, realMin: number
    let getTickPosition: (value: number) => THREE.Vector3
    let getTickEnd: (pos: THREE.Vector3) => THREE.Vector3
    let getLabelPosition: (pos: THREE.Vector3) => THREE.Vector3

    if (axis === 'x') {
      min = bounds.minX
      max = bounds.maxX
      realMin = realBounds.minX
      getTickPosition = (v) => new THREE.Vector3(v, bounds.minY, bounds.minZ)
      getTickEnd = (p) => new THREE.Vector3(p.x, p.y, p.z - 5)
      getLabelPosition = (p) => new THREE.Vector3(p.x, p.y - 5, p.z - 5)
    } else if (axis === 'y') {
      min = bounds.minY
      max = bounds.maxY
      realMin = realBounds.minY
      getTickPosition = (v) => new THREE.Vector3(bounds.minX, v, bounds.minZ)
      getTickEnd = (p) => new THREE.Vector3(p.x - 5, p.y, p.z)
      getLabelPosition = (p) => new THREE.Vector3(p.x - 5, p.y, p.z - 5)
    } else {
      min = bounds.minZ
      max = bounds.maxZ
      realMin = realBounds.minZ
      getTickPosition = (v) => new THREE.Vector3(bounds.minX, bounds.minY, v)
      getTickEnd = (p) => new THREE.Vector3(p.x - 5, p.y, p.z)
      getLabelPosition = (p) => new THREE.Vector3(p.x - 5, p.y - 5, p.z)
    }

    const range = max - min
    const numTicks = Math.ceil(range / tickInterval)

    for (let i = 0; i <= numTicks; i++) {
      const localValue = min + (i * tickInterval)
      if (localValue > max) break

      const realValue = realMin + (i * tickInterval)
      const tickPos = getTickPosition(localValue)
      const tickEnd = getTickEnd(tickPos)

      const geometry = new THREE.BufferGeometry().setFromPoints([tickPos, tickEnd])
      const material = new THREE.LineBasicMaterial({ color: 0x888888 })
      const tick = new THREE.Line(geometry, material)
      tick.name = `tick_${axis}_${i}`
      this._object.add(tick)

      const labelPos = getLabelPosition(tickPos)
      this.createTextSprite(
        realValue.toFixed(0), 
        labelPos, 
        0xCCCCCC,
        0.5
      )
    }
  }

  private createTextSprite(
    text: string, 
    position: THREE.Vector3, 
    color: number,
    scale: number = 1
  ) {
    const canvas = document.createElement('canvas')
    const context = canvas.getContext('2d')!
    canvas.width = 256
    canvas.height = 128

    context.fillStyle = `#${color.toString(16).padStart(6, '0')}`
    context.font = 'Bold 48px Arial'
    context.textAlign = 'center'
    context.textBaseline = 'middle'
    context.fillText(text, 128, 64)

    const texture = new THREE.CanvasTexture(canvas)
    const material = new THREE.SpriteMaterial({ map: texture })
    const sprite = new THREE.Sprite(material)
    sprite.position.copy(position)
    sprite.scale.set(10 * scale, 5 * scale, 1)
    this._object.add(sprite)
  }
}