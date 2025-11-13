import { Geo3DObject } from "./Geo3DObject"

class Geo3DFactory {
  private static registry: Record<string, new (props: any) => Geo3DObject> = {}

  static register(type: string, constructor: new (props: any) => Geo3DObject) {
    if (this.registry[type]) {
      console.warn(`Geo3D type "${type}" already registered. Overwriting.`)
    }
    this.registry[type] = constructor
  }

  static create(type: string, props: any): Geo3DObject {
    const ObjectClass = this.registry[type]
    
    if (!ObjectClass) {
      throw new Error(
        `Geo3D type "${type}" not registered. Available types: ${Object.keys(this.registry).join(', ')}`
      )
    }
    
    return new ObjectClass(props)
  }

  static isRegistered(type: string): boolean {
    return type in this.registry
  }

  static getRegisteredTypes(): string[] {
    return Object.keys(this.registry)
  }
}

export default Geo3DFactory