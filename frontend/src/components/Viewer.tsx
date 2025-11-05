import { FC } from "react"
import { Canvas } from "@react-three/fiber"
import { TrackballControls } from "@react-three/drei"
import { DrillholeData, computeBounds } from "../core/DrillHole"
import { Geo3DScene, SceneObject } from "../Geo3D/Geo3DScene"

interface ViewerProps {
  data: DrillholeData
}

export const Viewer: FC<ViewerProps> = ({ data }) => {
  const bounds = computeBounds(data)
  const centerX = (bounds.minX + bounds.maxX) / 2
  const centerY = (bounds.minY + bounds.maxY) / 2
  const centerZ = (bounds.minZ + bounds.maxZ) / 2

  // Recenter data to origin
  const localData: DrillholeData = {
    ...data,
    trajectories: data.trajectories.map(traj => ({
      ...traj,
      points: traj.points.map(p => ({
        ...p,
        x: p.x - centerX,
        y: p.y - centerY,
        z: p.z - centerZ,
      })),
    })),
  }

  const localBounds = {
    minX: bounds.minX - centerX,
    maxX: bounds.maxX - centerX,
    minY: bounds.minY - centerY,
    maxY: bounds.maxY - centerY,
    minZ: bounds.minZ - centerZ,
    maxZ: bounds.maxZ - centerZ,
  }

  const sceneObjects: SceneObject[] = [
    { 
      type: "boundingBox", 
      key: "bbox", 
      props: { bounds: localBounds } 
    },
    { 
      type: "grid",
      key: "grid", 
      props: { 
        bounds: localBounds,
        cellSize: 20,
        color: 0x6b7280,
        opacity: 0.4
      } 
    },
    { 
      type: "axes",
      key: "axes", 
      props: { 
        bounds: localBounds,
        realBounds: bounds,
        axisLength: 30,
        showTicks: true,
        tickInterval: 50,
      } 
    },
    ...localData.trajectories.map(traj => ({
      type: "drillhole",
      key: traj.hole_id,
      props: { 
        trajectory: traj,
        assays: data.assays,
        showCollar: true,
        showEndMarker: true,
      },
    })),
  ]
  
  // Camera 
  const sizeX = localBounds.maxX - localBounds.minX
  const sizeY = localBounds.maxY - localBounds.minY
  const sizeZ = localBounds.maxZ - localBounds.minZ
  const maxSize = Math.max(sizeX, sizeY, sizeZ)
  const cameraDistance = maxSize * 1.5

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Canvas
        camera={{ 
          position: [cameraDistance, cameraDistance, cameraDistance],
          fov: 60,
          near: 0.1,
          far: maxSize * 10 
        }}
        style={{ background: "#0f172a" }}
        gl={{ 
          antialias: true,
          alpha: false,
          powerPreference: "high-performance"
        }}
      >
        <Geo3DScene objects={sceneObjects} />
        <TrackballControls
          target={[0, 0, 0]}
          dynamicDampingFactor={0.1}
          rotateSpeed={2.0}
          zoomSpeed={1.2}
          panSpeed={0.8}
          minDistance={maxSize * 0.3}
          maxDistance={maxSize * 5}
          noZoom={false}
          noPan={false}
          noRotate={false}
        />
      </Canvas>
    </div>
  )
}