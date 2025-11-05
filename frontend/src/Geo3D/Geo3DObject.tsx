import * as THREE from "three"

export abstract class Geo3DObject {
  protected _object: THREE.Object3D
  protected _disposed = false

  constructor() {
    this._object = new THREE.Group()
    this._object.name = this.constructor.name
  }

  getObject(): THREE.Object3D {
    return this._object
  }

  add(child: THREE.Object3D | Geo3DObject) {
    if (child instanceof Geo3DObject) {
      this._object.add(child.getObject())
    } else {
      this._object.add(child)
    }
  }

  remove(child: THREE.Object3D | Geo3DObject) {
    if (child instanceof Geo3DObject) {
      this._object.remove(child.getObject())
    } else {
      this._object.remove(child)
    }
  }

  dispose() {
    if (this._disposed) return
    
    this._object.traverse((obj) => {
      if (obj instanceof THREE.Mesh) {
        obj.geometry?.dispose()
        if (Array.isArray(obj.material)) {
          obj.material.forEach(m => m.dispose())
        } else {
          obj.material?.dispose()
        }
      } else if (obj instanceof THREE.Line) {
        obj.geometry?.dispose()
        if (Array.isArray(obj.material)) {
          obj.material.forEach(m => m.dispose())
        } else {
          obj.material?.dispose()
        }
      }
    })
    
    this._disposed = true
  }

  setVisible(visible: boolean) {
    this._object.visible = visible
  }

  setPosition(x: number, y: number, z: number) {
    this._object.position.set(x, y, z)
  }
}