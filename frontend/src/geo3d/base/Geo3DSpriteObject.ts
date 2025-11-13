import { Geo3DObject } from "./Geo3DObject";
import * as THREE from 'three'

export class Geo3DSpriteObject extends Geo3DObject {

    updateSpriteScales(camera: THREE.Camera) {
        this._object.traverse(o => {
            if (o instanceof THREE.Sprite) {
            const dist = camera.position.distanceTo(o.position)
            const scale = dist * 0.15
            o.scale.set(scale, scale * 0.5, 1)
            }
        })
    }
}