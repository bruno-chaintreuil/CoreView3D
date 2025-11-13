import * as THREE from "three"

export interface TextSpriteConfig {
  text: string
  position: THREE.Vector3
  color?: number | string
  bold?: boolean
  fontSize?: number
  background?: boolean
  backgroundColor?: string
  padding?: number
  transparent?: boolean
  depthTest?: boolean
  depthWrite?: boolean
  canvasWidth?: number
  canvasHeight?: number
}

export class TextSprite {
  public object: THREE.Sprite
  private canvas: HTMLCanvasElement
  private ctx: CanvasRenderingContext2D
  private config: Required<TextSpriteConfig>

  constructor(config: TextSpriteConfig) {
    const defaults: Required<Omit<TextSpriteConfig, "text" | "position">> = {
      color: 0xffffff,
      bold: false,
      fontSize: config.bold ? 64 : 52,
      background: false,
      backgroundColor: "rgba(15, 23, 42, 0.8)",
      padding: 15,
      transparent: true,
      depthTest: false,
      depthWrite: false,
      canvasWidth: 512,
      canvasHeight: 256,
    }

    this.config = { ...defaults, ...config }

    this.canvas = document.createElement("canvas")
    this.canvas.width = this.config.canvasWidth
    this.canvas.height = this.config.canvasHeight
    this.ctx = this.canvas.getContext("2d", { alpha: true })!

    const texture = new THREE.CanvasTexture(this.canvas)
    texture.minFilter = THREE.LinearFilter
    texture.magFilter = THREE.LinearFilter

    const material = new THREE.SpriteMaterial({
      map: texture,
      transparent: this.config.transparent,
      depthTest: this.config.depthTest,
      depthWrite: this.config.depthWrite,
    })

    this.object = new THREE.Sprite(material)
    this.object.position.copy(config.position)

    this.render()
  }

  private render() {
    const { text, bold, fontSize, color, background, backgroundColor, padding } = this.config
    const { canvas, ctx } = this

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    if (background) {
      ctx.fillStyle = backgroundColor
      ctx.fillRect(0, 0, canvas.width, canvas.height)
    }

    const colorStr =
      typeof color === "number" ? `#${color.toString(16).padStart(6, "0")}` : color

    ctx.font = `${bold ? "bold" : "normal"} ${fontSize}px Arial`
    ctx.textAlign = "center"
    ctx.textBaseline = "middle"
    ctx.lineWidth = bold ? 4 : 3
    ctx.strokeStyle = "rgba(0,0,0,0.5)"
    ctx.fillStyle = colorStr
    const x = canvas.width / 2
    const y = canvas.height / 2
    ctx.strokeText(text, x, y)
    ctx.fillText(text, x, y)

    const mat = this.object.material as THREE.SpriteMaterial
    mat.map!.needsUpdate = true
  }

  updateText(newText: string) {
    this.config.text = newText
    this.render()
  }

  updateColor(newColor: number | string) {
    this.config.color = newColor
    this.render()
  }

  setPosition(pos: THREE.Vector3) {
    this.object.position.copy(pos)
  }
}
