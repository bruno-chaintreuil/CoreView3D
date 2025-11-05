// Geo3D/Geo3DRegistry.ts
import Geo3DFactory from './Geo3DFactory'
import { Geo3DDrillhole } from './Geo3DDrillhole'
import { Geo3DBoundingBox } from './Geo3DBoundingBox'
import { Geo3DGrid } from './Geo3DGrid'
import { Geo3DAxes } from './Geo3DAxisWidget'

export function initializeGeo3DObjects() {
  Geo3DFactory.register('drillhole', Geo3DDrillhole)
  Geo3DFactory.register('boundingBox', Geo3DBoundingBox)
  Geo3DFactory.register('grid', Geo3DGrid)
  Geo3DFactory.register('axes', Geo3DAxes)

  console.log(`Registered Geo3D types: ${Geo3DFactory.getRegisteredTypes().join(', ')}`)
}