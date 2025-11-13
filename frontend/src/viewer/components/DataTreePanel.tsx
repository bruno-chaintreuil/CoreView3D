import { FC, useState, useMemo } from 'react'
import { 
  Tree, 
  TreeNodeInfo, 
  Checkbox,
  Card,
  Divider,
  Classes,
  Tag
} from '@blueprintjs/core'
import { DrillholeData } from '../../drillholes/base/DrillHole'
import { useViewerStore } from '../base/useViewerStore'

interface DataTreePanelProps {
  data: DrillholeData
}

interface CustomNodeData {
  type: 'category' | 'drillhole' | 'option' | 'stat'
  holeId?: string
}

function getDrillholeColor(holeId: string): string {
  const hue = Math.abs(
    holeId.split('').reduce((a, b) => a + b.charCodeAt(0), 0)
  ) % 360
  return `hsl(${hue}, 70%, 50%)`
}

export const DataTreePanel: FC<DataTreePanelProps> = ({data}) => {
  const { setVisibleHoles, hideAllHoles, visibleHoles, toggleHole, showAxes, setShowAxes, showEndMarkers, setShowEndMarkers, showCollars, setShowCollars, showBoundingBox, setShowBoundingBox, showGrid, setShowGrid, showLabels, setShowLabels } = useViewerStore()
  
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedIds, setExpandedIds] = useState<Set<string>>(
    new Set(['drillholes', 'display', 'scene', 'stats'])
  )

  const handleToggleAll = (visible: boolean) => {
    if (visible) {
      setVisibleHoles(new Set(data.trajectories.map(t => t.hole_id)))
    } else {
      hideAllHoles()
    }
  }

  const filteredHoles = useMemo(() => {
    if (!searchTerm) return data.trajectories
    const lower = searchTerm.toLowerCase()
    return data.trajectories.filter(t => 
      t.hole_id.toLowerCase().includes(lower)
    )
  }, [data.trajectories, searchTerm])

  const stats = useMemo(() => {
    const totalDepth = data.trajectories.reduce(
      (sum, t) => sum + t.collar.max_depth, 0
    )
    return {
      total: data.trajectories.length,
      visible: visibleHoles.size,
      totalDepth: totalDepth.toFixed(0),
      assays: data.assays?.length || 0,
    }
  }, [data, visibleHoles])

  const treeNodes: TreeNodeInfo<CustomNodeData>[] = useMemo(() => {
    const nodes: TreeNodeInfo<CustomNodeData>[] = []

    const allVisible = filteredHoles.length > 0 && filteredHoles.every(t => visibleHoles.has(t.hole_id))

    const drillholesNode: TreeNodeInfo<CustomNodeData> = {
      id: 'drillholes',
      label: (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
          <span>Drillholes ({data.trajectories.length})</span>
          <Checkbox
            checked={allVisible}
            onChange={(e) => {
              e.stopPropagation()
              handleToggleAll(!allVisible)
            }}
            style={{ margin: 0 }}
            title="Toggle all drillholes"
          />
        </div>
      ),
      icon: 'geosearch',
      isExpanded: expandedIds.has('drillholes'),
      nodeData: { type: 'category' },
      childNodes: filteredHoles.map(traj => {
        const isVisible = visibleHoles.has(traj.hole_id)
        return {
          id: `hole_${traj.hole_id}`,
          label: (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '100%' }}>
              <div style={{
                width: '10px',
                height: '10px',
                borderRadius: '2px',
                background: getDrillholeColor(traj.hole_id),
                flexShrink: 0
              }} />
              <span style={{ flex: 1 }}>{traj.hole_id}</span>
              <Tag minimal round>{traj.collar.max_depth.toFixed(0)}m</Tag>
            </div>
          ),
          icon: (
            <Checkbox
              checked={isVisible}
              onChange={() => toggleHole(traj.hole_id)}
              style={{ margin: 0 }}
            />
          ),
          nodeData: { type: 'drillhole', holeId: traj.hole_id },
        }
      }),
    }
    nodes.push(drillholesNode)

    nodes.push({
      id: 'display',
      label: 'Display Options',
      icon: 'eye-open',
      isExpanded: expandedIds.has('display'),
      nodeData: { type: 'category' },
      childNodes: [
        {
          id: 'opt_collars',
          label: 'Show Collars',
          icon: <Checkbox checked={showCollars} onChange={() => setShowCollars(!showCollars)} />,
          nodeData: { type: 'option' },
        },
        {
          id: 'opt_labels',
          label: 'Show Labels',
          icon: <Checkbox checked={showLabels} onChange={() => setShowLabels(!showLabels)} />,
          nodeData: { type: 'option' },
        },
        {
          id: 'opt_endmarkers',
          label: 'Show End Markers',
          icon: <Checkbox checked={showEndMarkers} onChange={() => setShowEndMarkers(!showEndMarkers)} />,
          nodeData: { type: 'option' },
        },
      ],
    })

    nodes.push({
      id: 'scene',
      label: 'Scene Elements',
      icon: 'cube',
      isExpanded: expandedIds.has('scene'),
      nodeData: { type: 'category' },
      childNodes: [
        {
          id: 'scene_grid',
          label: 'Grid',
          icon: <Checkbox checked={showGrid} onChange={() => setShowGrid(!showGrid)} />,
          nodeData: { type: 'option' },
        },
        {
          id: 'scene_bbox',
          label: 'Bounding Box',
          icon: <Checkbox checked={showBoundingBox} onChange={( ()=> setShowBoundingBox(!showBoundingBox))} />,
          nodeData: { type: 'option' },
        },
        {
          id: 'scene_axes',
          label: 'Axes',
          icon: <Checkbox checked={showAxes} onChange={() => setShowAxes(!showAxes)} />,
          nodeData: { type: 'option' },
        },
      ],
    })

    const statsChildren: TreeNodeInfo<CustomNodeData>[] = [
      {
        id: 'stat_total',
        label: `Total Holes: ${stats.total}`,
        icon: 'numerical',
        nodeData: { type: 'stat' },
      },
      {
        id: 'stat_visible',
        label: `Visible: ${stats.visible}`,
        icon: 'eye-open',
        nodeData: { type: 'stat' },
      },
      {
        id: 'stat_depth',
        label: `Total Depth: ${stats.totalDepth} m`,
        icon: 'vertical-distribution',
        nodeData: { type: 'stat' },
      },
    ]

    if (stats.assays > 0) {
      statsChildren.push({
        id: 'stat_assays',
        label: `Assay Intervals: ${stats.assays}`,
        icon: 'lab-test',
        nodeData: { type: 'stat' },
      })
    }

    nodes.push({
      id: 'stats',
      label: 'Statistics',
      icon: 'chart',
      isExpanded: expandedIds.has('stats'),
      nodeData: { type: 'category' },
      childNodes: statsChildren,
    })

    return nodes
  }, [
    data.trajectories,
    filteredHoles,
    visibleHoles,
    expandedIds,
    showCollars,
    showLabels,
    showEndMarkers,
    showGrid,
    showBoundingBox,
    showAxes,
    stats,
    handleToggleAll,
    toggleHole,
    setShowCollars,
    setShowLabels,
    setShowEndMarkers,
    setShowGrid,
    setShowBoundingBox,
    setShowAxes
  ])

  const handleNodeClick = (
    node: TreeNodeInfo<CustomNodeData>,
    _nodePath: number[],
    e: React.MouseEvent
  ) => {
    e.stopPropagation()
    if (node.nodeData?.type === 'drillhole' && node.nodeData.holeId) {
      toggleHole(node.nodeData.holeId)
    }
  }

  const handleNodeCollapse = (node: TreeNodeInfo<CustomNodeData>) => {
    setExpandedIds(prev => {
      const next = new Set(prev)
      next.delete(node.id.toString())
      return next
    })
  }

  const handleNodeExpand = (node: TreeNodeInfo<CustomNodeData>) => {
    setExpandedIds(prev => {
      const next = new Set(prev)
      next.add(node.id.toString())
      return next
    })
  }

  return (
    <Card 
      className={Classes.DARK}
      style={{ 
        width: '320px',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        margin: 0,
        borderRadius: 0,
        overflow: 'hidden'
      }}
    >
      <div style={{ padding: '3px' }}>
        <h6 className={Classes.HEADING}>
          Data Tree
          <Tag minimal intent="primary" style={{ marginLeft: '10px' }}>
            {stats.visible}/{stats.total}
          </Tag>
        </h6>
      </div>
      <Divider style={{ margin: 0 }} />
      <div style={{ flex: 1, overflowY: 'auto', padding: '10px' }}>
        <Tree
          contents={treeNodes}
          onNodeClick={handleNodeClick}
          onNodeCollapse={handleNodeCollapse}
          onNodeExpand={handleNodeExpand}
          className={Classes.DARK}
        />
      </div>
    </Card>
  )
}