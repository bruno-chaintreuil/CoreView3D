import { FC } from 'react'
import { Classes, Tag } from '@blueprintjs/core'
import { useViewerStore } from '../base/useViewerStore'

export const StatusBar: FC = () => {
  const { mousePosition, visibleHoles } = useViewerStore()

  return (
    <div 
      className={Classes.DARK}
      style={{
        height: '32px',
        background: '#1C2127',
        borderTop: '1px solid #2F343C',
        display: 'flex',
        alignItems: 'center',
        padding: '0 16px',
        gap: '24px',
        fontSize: '12px',
        color: '#8A9BA8'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span style={{ fontWeight: 600 }}>CoreView3D</span>
        <Tag minimal>v0.1.0</Tag>
      </div>

      <div style={{ width: '1px', height: '20px', background: '#2F343C' }} />

      <div>
        Position: 
        <strong style={{ color: '#10B981', marginLeft: '6px' }}>
          E: {mousePosition.x.toFixed(1)}
        </strong>
        <strong style={{ color: '#f63b3bff', marginLeft: '12px' }}>
          N: {mousePosition.y.toFixed(1)}
        </strong>
        <strong style={{ color: '#3B82F6', marginLeft: '12px' }}>
          Z: {mousePosition.z.toFixed(1)}
        </strong>
      </div>

      <div style={{ flex: 1 }} />

      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <span style={{ fontSize: '11px', color: '#64748b' }}>
          Left: Rotate • Right: Pan • Scroll: Zoom
        </span>
        <div style={{ width: '1px', height: '20px', background: '#2F343C' }} />
        <a 
          href="https://github.com/bruno-chaintreuil/CoreView3D" 
          target="_blank" 
          rel="noopener noreferrer"
          style={{ color: '#48AFF0', textDecoration: 'none' }}
        >
          GitHub
        </a>
      </div>
    </div>
  )
}