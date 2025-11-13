import * as THREE from 'three'
import { TrajectoryPoint } from '../../utils/Trajectory'

export function interpolatePointAtDepth(
  points: TrajectoryPoint[],
  targetDepth: number
): THREE.Vector3 {
  if (points.length === 0) return new THREE.Vector3()

  const minDepth = points[0].depth
  const maxDepth = points[points.length - 1].depth
  const clampedDepth = Math.min(Math.max(targetDepth, minDepth), maxDepth)

  let p1 = points[0]
  let p2 = points[points.length - 1]

  for (let i = 0; i < points.length - 1; i++) {
    if (points[i].depth <= clampedDepth && points[i + 1].depth >= clampedDepth) {
      p1 = points[i]
      p2 = points[i + 1]
      break
    }
  }

  const t = p2.depth !== p1.depth ? (clampedDepth - p1.depth) / (p2.depth - p1.depth) : 0
  return new THREE.Vector3(
    p1.x + t * (p2.x - p1.x),
    p1.y + t * (p2.y - p1.y),
    p1.z + t * (p2.z - p1.z)
  )
}

export function getPointsInInterval(
  points: TrajectoryPoint[],
  fromDepth: number,
  toDepth: number
): THREE.Vector3[] {
  const minDepth = points[0].depth
  const maxDepth = points[points.length - 1].depth
  const from = Math.max(fromDepth, minDepth)
  const to = Math.min(toDepth, maxDepth)
  return points
    .filter(p => p.depth > from && p.depth < to)
    .map(p => new THREE.Vector3(p.x, p.y, p.z))
}
