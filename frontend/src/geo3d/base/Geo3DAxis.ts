import * as THREE from "three"
import { Geo3DSpriteObject } from "./Geo3DSpriteObject"
import { TextSprite } from "./Geo3DTextSprite"
import { Bounds } from "../../utils/base/Bounds"

export interface Geo3DAxesOptions {
  bounds: Bounds
  realBounds: Bounds
  showAxes?: boolean
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
    
    const defaultTickSize = 2; 
    
    this.options = {
      bounds: options.bounds,
      realBounds: options.realBounds,
      showAxes: options.showAxes ?? true,
      axisLength: options.axisLength ?? 60, 
      showTicks: options.showTicks ?? true,
      tickInterval: options.tickInterval ?? 100,
      tickSize: options.tickSize ?? defaultTickSize, 
      colors: options.colors ?? { x: 0xef4444, y: 0x10b981, z: 0x3b82f6 },
    }
    this.build()
  }

  private build() {
    if (this.options.showAxes) {
      this.createAxis("x", "EASTING", new THREE.Vector3(1, 0, 0))
      this.createAxis("y", "NORTHING", new THREE.Vector3(0, 1, 0))
      this.createAxis("z", "DEPTH (RL)", new THREE.Vector3(0, 0, -1))
    }
    
    if (this.options.showTicks) {
      this.createTicks()
    }
  }

  private createAxis(axis: "x" | "y" | "z", label: string, direction: THREE.Vector3) {
    const { bounds, options } = this
    const { axisLength, colors } = options
    const originSurface = new THREE.Vector3(bounds.minX, bounds.minY, bounds.maxZ)

    let start: THREE.Vector3, end: THREE.Vector3, labelPos: THREE.Vector3, color: number

    if (axis === "x") {
      start = originSurface.clone()
      end = new THREE.Vector3(bounds.maxX + axisLength, bounds.minY, bounds.maxZ)
      labelPos = new THREE.Vector3(bounds.maxX + axisLength + 30, bounds.minY, bounds.maxZ)
      color = colors.x
    } else if (axis === "y") {
      start = originSurface.clone()
      end = new THREE.Vector3(bounds.minX, bounds.maxY + axisLength, bounds.maxZ)
      labelPos = new THREE.Vector3(bounds.minX, bounds.maxY + axisLength + 30, bounds.maxZ)
      color = colors.y
    } else {
      start = originSurface.clone()
      end = new THREE.Vector3(bounds.minX, bounds.minY, bounds.minZ - axisLength)
      labelPos = new THREE.Vector3(bounds.minX, bounds.minY, bounds.minZ - axisLength - 30)
      color = colors.z
    }

    const geometry = new THREE.BufferGeometry().setFromPoints([start, end])
    const material = new THREE.LineBasicMaterial({ color, linewidth: 4 })
    this._object.add(new THREE.Line(geometry, material))

    const arrowHelper = new THREE.ArrowHelper(direction, end, 20, color, 12, 8)
    this._object.add(arrowHelper)

    this.addTextSprite(label, labelPos, color, 3.0, true)
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
      min = bounds.minX; max = bounds.maxX; realMin = realBounds.minX
      getTickPosition = (v) => new THREE.Vector3(v, bounds.minY, bounds.maxZ)
      getTickEnd = (p) => new THREE.Vector3(p.x, p.y, p.z + tickSize)
      getLabelPosition = (p) => new THREE.Vector3(p.x, p.y, p.z + tickSize + 8)
    } else if (axis === "y") {
      min = bounds.minY; max = bounds.maxY; realMin = realBounds.minY
      getTickPosition = (v) => new THREE.Vector3(bounds.minX, v, bounds.maxZ)
      getTickEnd = (p) => new THREE.Vector3(p.x, p.y, p.z + tickSize)
      getLabelPosition = (p) => new THREE.Vector3(p.x, p.y, p.z + tickSize + 8)
    } else {
      min = bounds.minZ; max = bounds.maxZ; realMin = realBounds.minZ
      getTickPosition = (v) => new THREE.Vector3(bounds.minX, bounds.minY, v)
      getTickEnd = (p) => new THREE.Vector3(p.x - tickSize, p.y, p.z)
      getLabelPosition = (p) => new THREE.Vector3(p.x - (tickSize + 15), p.y, p.z)
    }

    const range = max - min
    const numTicks = Math.floor(range / tickInterval)

    for (let i = 0; i <= numTicks; i++) {
      let localValue: number, displayValue: number

      if (axis === "z") {
        localValue = max - (i * tickInterval)
        displayValue = realMin + (i * tickInterval)
      } else {
        localValue = min + (i * tickInterval)
        displayValue = realMin + (i * tickInterval)
      }
      
      const tickPos = getTickPosition(localValue)
      const tickEnd = getTickEnd(tickPos)

      const geometry = new THREE.BufferGeometry().setFromPoints([tickPos, tickEnd])
      const material = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.8 })
      this._object.add(new THREE.Line(geometry, material))

      const labelPos = getLabelPosition(tickPos)
      this.addTextSprite(displayValue.toFixed(0), labelPos, 0xffffff, 1.6)
    }
  }

  private addTextSprite(text: string, position: THREE.Vector3, color: number, scale: number, bold = false) {
    const sprite = new TextSprite({
      text,
      position,
      color,
      fontSize: 32, 
      bold,
      depthTest: false,
    })
    
    const baseScale = scale * 18;
    sprite.object.scale.set(baseScale, baseScale, 1) 
    this.spriteList.push(sprite.object)
    this._object.add(sprite.object)
  }

  /**
   * Overriding the update function from Geo3DSpriteObject 
   * to ensure labels face the camera correctly.
  */
  public updateSpriteScales(camera: THREE.Camera) {
    this.spriteList.forEach(sprite => {
    })
  }
}