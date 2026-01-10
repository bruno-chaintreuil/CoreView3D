import { FC, useMemo } from 'react'
import { CrossSectionData } from '../session/base/useCrossSection'

interface ChartProps {
  data: CrossSectionData
  width: number
  height: number
}

export const CrossSectionChart: FC<ChartProps> = ({ data, width, height }) => {
  const margin = { top: 40, right: 40, bottom: 60, left: 80 }

  const { toScreenX, toScreenZ, ticksX, ticksZ } = useMemo(() => {
    const allX = data.drillholes.flatMap(h => h.trace.map(p => p.x))
    const allZ = data.drillholes.flatMap(h => h.trace.map(p => p.z))
    
    if (!allX.length) return { toScreenX: () => 0, toScreenZ: () => 0, ticksX: [], ticksZ: [] }

    const minX = Math.min(...allX), maxX = Math.max(...allX)
    const minZ = Math.min(...allZ), maxZ = Math.max(...allZ)
    
    const rangeX = maxX - minX || 1
    const rangeZ = maxZ - minZ || 1
    
    const scaleX = (width - margin.left - margin.right) / rangeX
    const scaleZ = (height - margin.top - margin.bottom) / rangeZ

    const toScreenX = (x: number) => margin.left + (x - minX) * scaleX
    const toScreenZ = (z: number) => margin.top + (height - margin.top - margin.bottom) - (z - minZ) * scaleZ

    const ticksX = Array.from({ length: 11 }, (_, i) => minX + (rangeX / 10) * i)
    const ticksZ = Array.from({ length: 11 }, (_, i) => minZ + (rangeZ / 10) * i)

    return { toScreenX, toScreenZ, ticksX, ticksZ }
  }, [data, width, height])

  return (
    <svg width={width} height={height} style={{ background: '#1C2127', display: 'block' }}>
      <g className="grid">
        {ticksX.map((x, i) => (
          <g key={`x-${i}`}>
            <line x1={toScreenX(x)} y1={margin.top} x2={toScreenX(x)} y2={height - margin.bottom} stroke="#374151" strokeDasharray="4" />
            <text x={toScreenX(x)} y={height - margin.bottom + 20} fill="#8A9BA8" fontSize="11" textAnchor="middle">{x.toFixed(0)}</text>
          </g>
        ))}
        {ticksZ.map((z, i) => (
          <g key={`z-${i}`}>
            <line x1={margin.left} y1={toScreenZ(z)} x2={width - margin.right} y2={toScreenZ(z)} stroke="#374151" strokeDasharray="4" />
            <text x={margin.left - 10} y={toScreenZ(z) + 4} fill="#8A9BA8" fontSize="11" textAnchor="end">{z.toFixed(0)}</text>
          </g>
        ))}
      </g>

      <text x={width / 2} y={height - 20} fill="#CBD5E1" fontSize="14" textAnchor="middle">Distance (m)</text>
      <text x={20} y={height / 2} fill="#CBD5E1" fontSize="14" textAnchor="middle" transform={`rotate(-90, 20, ${height / 2})`}>Elevation (m)</text>

      {data.drillholes.map(hole => {
        if (!hole.trace?.length) return null
        const points = hole.trace.map(p => `${toScreenX(p.x)},${toScreenZ(p.z)}`).join(' ')
        const start = hole.trace[0]
        
        return (
          <g key={hole.hole_id}>
            <polyline points={points} fill="none" stroke="#60a5fa" strokeWidth={2} />
            <circle cx={toScreenX(start.x)} cy={toScreenZ(start.z)} r={4} fill="#FFD700" stroke="#1C2127" strokeWidth={2} />
            <text x={toScreenX(start.x)} y={toScreenZ(start.z) - 10} fill="#F5F8FA" fontSize="12" textAnchor="middle" fontWeight="bold">
              {hole.hole_id}
            </text>
          </g>
        )
      })}
    </svg>
  )
}