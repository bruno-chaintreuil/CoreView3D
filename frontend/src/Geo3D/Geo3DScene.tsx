import { FC, useMemo, useEffect } from "react"
import Geo3DFactory from "./Geo3DFactory"

export interface SceneObject {
  key: string
  type: string
  props: Record<string, any>
}

interface Geo3DSceneProps {
  objects: SceneObject[]
}

export const Geo3DScene: FC<Geo3DSceneProps> = ({ objects }) => {
  const sceneObjects = useMemo(() => {
    return objects.map(obj => {
      try {
        const instance = Geo3DFactory.create(obj.type, obj.props)
        return {
          key: obj.key,
          object: instance.getObject(),
          instance,
        }
      } catch (error) {
        console.error(`Failed to create Geo3D object:`, error)
        return null
      }
    }).filter(Boolean)
  }, [objects])

  useEffect(() => {
    return () => {
      sceneObjects.forEach(obj => obj?.instance.dispose())
    }
  }, [sceneObjects])

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[100, 100, 100]} intensity={1} />
      <directionalLight position={[-100, -100, -100]} intensity={0.3} />
      
      {sceneObjects.map(obj => obj && (
        <primitive key={obj.key} object={obj.object} />
      ))}
    </>
  )
}