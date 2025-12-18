import { FC, useMemo, useEffect } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { TrackballControls } from '@react-three/drei'
import * as THREE from 'three'
import { DrillholeData, DrillholeTrajectory } from '../../drillholes/base/DrillHole'
import { Geo3DScene, SceneObject } from '../../geo3d/components/Geo3DScene'
import { CameraController } from '../base/CameraController'
import { useViewerStore } from '../base/useViewerStore'
import { TrajectoryPoint } from '../../utils/base/Trajectory'

const ClickHandler: FC<{ onDrillholeClick: (holeId: string) => void }> = ({ 
  onDrillholeClick 
}) => {
  const { camera, scene, gl } = useThree()
  
  useEffect(() => {
    const raycaster = new THREE.Raycaster()
    raycaster.params.Line = { threshold: 2 }
    
    const handleClick = (event: MouseEvent) => {
      const rect = gl.domElement.getBoundingClientRect()
      
      const mouse = new THREE.Vector2(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1
      )

      raycaster.setFromCamera(mouse, camera)
      const intersects = raycaster.intersectObjects(scene.children, true)

      if (intersects.length > 0) {
        const clicked = intersects[0].object
        
        let current: THREE.Object3D | null = clicked
        while (current) {
          if (current.name && (
            current.name.startsWith('trajectory_') ||
            current.name.startsWith('segment_') ||
            current.name.startsWith('collar_') ||
            current.name.startsWith('label_')
          )) {
            const parts = current.name.split('_')
            if (parts.length >= 2) {
              const holeId = parts.slice(1).join('_')
              onDrillholeClick(holeId)
              break
            }
          }
          current = current.parent
        }
      }
    }

    const handleMouseMove = (event: MouseEvent) => {
      const rect = gl.domElement.getBoundingClientRect()
      
      const mouse = new THREE.Vector2(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1
      )

      raycaster.setFromCamera(mouse, camera)
      
      // Intersect with a ground plane at z=0 (or the grid level)
      const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0)
      const intersection = new THREE.Vector3()
      raycaster.ray.intersectPlane(plane, intersection)
      
      if (intersection) {
        // Need to pass onMouseMove from props
        // onMouseMove({ x: intersection.x, y: intersection.y, z: intersection.z })
      }
    }
    
    gl.domElement.addEventListener('click', handleClick)
    gl.domElement.addEventListener('mousemove', handleMouseMove)
    
    return () => {
      gl.domElement.removeEventListener('click', handleClick)
      gl.domElement.removeEventListener('mousemove', handleMouseMove)
    }
  }, [camera, scene, gl, onDrillholeClick])
  
  return null
}

interface ViewerCanvasProps {
  data: DrillholeData
}


export const ViewerCanvas: FC<ViewerCanvasProps> = ({ data }) => {  
  const {
    visibleHoles,
    selectedHoleId,
    showCollars,
    showLabels,
    showEndMarkers,
    showGrid,
    showBoundingBox,
    showAxes,
    setSelectedHoleId,
    zScale
  } = useViewerStore()
  
  const bounds = data.computeBounds()
  const centerX = (bounds.minX + bounds.maxX) / 2
  const centerY = (bounds.minY + bounds.maxY) / 2
  const centerZ = (bounds.minZ + bounds.maxZ) / 2

  const localData: DrillholeData = useMemo(() => {
    const trajectories = data.trajectories.map(traj => {
      const localPoints: TrajectoryPoint[] = traj.points.map(p => ({
        ...p,
        x: p.x - centerX,
        y: p.y - centerY,
        z: p.z - centerZ,
      }))
            const localTraj = new DrillholeTrajectory(
        traj.hole_id,
        {
          Hole_ID: traj.hole_id,
          East: traj.collar.east,
          North: traj.collar.north,
          Elevation: traj.collar.elevation,
          Max_Depth: traj.collar.max_depth,
          Azimuth: traj.collar.azimuth,
          Dip: traj.collar.dip,
        },
        localPoints,
        traj.has_survey
      )
      return localTraj
    })
    const assays = data.assays ?? []
    return new DrillholeData(trajectories, assays)
  }, [data, centerX, centerY, centerZ])  

  const localBounds = useMemo(() => ({
    minX: bounds.minX - centerX,
    maxX: bounds.maxX - centerX,
    minY: bounds.minY - centerY,
    maxY: bounds.maxY - centerY,
    minZ: bounds.minZ - centerZ,
    maxZ: bounds.maxZ - centerZ,
  }), [bounds, centerX, centerY, centerZ])

  const sceneObjects: SceneObject[] = useMemo(() => {
    const objects: SceneObject[] = []
    
    if (showBoundingBox) {
      objects.push({ 
        type: "boundingBox", 
        key: "bbox", 
        props: { bounds: localBounds } 
      })
    }
    
    if (showGrid) {
      objects.push({ 
        type: "grid",
        key: "grid", 
        props: { 
          bounds: localBounds,
          cellSize: 20,
          color: 0x6b7280,
          opacity: 0.4
        } 
      })
    }
    
    if (showAxes) {
      objects.push({ 
        type: "axes",
        key: "axes", 
        props: { 
          bounds: localBounds,
          realBounds: bounds,
          axisLength: 30,
          showTicks: true,
          tickInterval: 50,
        } 
      })
    }

    localData.trajectories
    .filter(traj => visibleHoles.has(traj.hole_id))
    .forEach(traj => {
      const holeAssays = data.assays?.filter(a => a.Hole_ID === traj.hole_id) ?? []
      objects.push({
        type: "drillhole",
        key: traj.hole_id,
        props: { 
          trajectory: traj,
          assays: holeAssays,
          showCollar: showCollars,
          showEndMarker: showEndMarkers,
          showLabel: showLabels,
        },
      })
    })

    return objects
  }, [
    localData.trajectories,
    visibleHoles,
    data.assays,
    localBounds,
    bounds,
    showBoundingBox,
    showGrid,
    showAxes,
    showCollars,
    showEndMarkers,
    showLabels,
  ])

  const sizeX = localBounds.maxX - localBounds.minX
  const sizeY = localBounds.maxY - localBounds.minY
  const sizeZ = localBounds.maxZ - localBounds.minZ
  const maxSize = Math.max(sizeX, sizeY, sizeZ)
  const cameraDistance = maxSize * 1.5

  const handleDrillholeClick = (holeId: string) => {
    setSelectedHoleId(selectedHoleId === holeId ? null : holeId)
  }

  return (
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
        powerPreference: "high-performance",
        preserveDrawingBuffer: true,
      }}
    >
      <CameraController bounds={localBounds} />
        <group scale={[1, 1, zScale]}>
          <Geo3DScene objects={sceneObjects} />
        </group>
      <ClickHandler onDrillholeClick={handleDrillholeClick} />  
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
  )
}