import { FC, useEffect, useRef } from 'react'
import { useThree, useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useViewerStore, CameraView } from './useViewerStore'

interface CameraControllerProps {
  bounds: {
    minX: number
    maxX: number
    minY: number
    maxY: number
    minZ: number
    maxZ: number
  }
}

export const CameraController: FC<CameraControllerProps> = ({ bounds }) => {
  const { camera } = useThree()
  const { cameraView, cameraState, setCameraState } = useViewerStore()
  
  const animatingRef = useRef(false)
  const startPosRef = useRef<THREE.Vector3 | null>(null)
  const targetPosRef = useRef<THREE.Vector3 | null>(null)
  const startTimeRef = useRef(0)
  const durationRef = useRef(500) 

  const sizeX = bounds.maxX - bounds.minX
  const sizeY = bounds.maxY - bounds.minY
  const sizeZ = bounds.maxZ - bounds.minZ
  const maxSize = Math.max(sizeX, sizeY, sizeZ)
  const distance = maxSize * 1.5

  useEffect(() => {
    if (cameraState && !animatingRef.current) {
      camera.position.set(...cameraState.position)
      camera.lookAt(new THREE.Vector3(...cameraState.target))
    }
  }, [cameraState, camera])

  useEffect(() => {
    if (!cameraView) return

    const target = new THREE.Vector3(0, 0, 0)
    let position: THREE.Vector3

    switch (cameraView) {
      case 'top':
        position = new THREE.Vector3(0, 0, distance * 1.2)
        break
      case 'front':
        position = new THREE.Vector3(0, distance * 1.2, 0)
        break
      case 'side':
        position = new THREE.Vector3(distance * 1.2, 0, 0)
        break
      case 'iso':
      case 'reset':
      default:
        position = new THREE.Vector3(distance, distance, distance)
        break
    }

    startPosRef.current = camera.position.clone()
    targetPosRef.current = position
    startTimeRef.current = Date.now()
    animatingRef.current = true    
  }, [cameraView, distance, camera])

  useFrame(() => {
    if (!animatingRef.current || !startPosRef.current || !targetPosRef.current) {
      return
    }

    const elapsed = Date.now() - startTimeRef.current
    const t = Math.min(elapsed / durationRef.current, 1)

    const eased = 1 - Math.pow(1 - t, 3)
    camera.position.lerpVectors(startPosRef.current, targetPosRef.current, eased)
    camera.lookAt(0, 0, 0)

    if (t >= 1) {
      animatingRef.current = false
      setCameraState({
        position: [camera.position.x, camera.position.y, camera.position.z],
        target: [0, 0, 0],
      })
    }
  })

  return null
}