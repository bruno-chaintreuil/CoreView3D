import { FC, useState } from 'react'
import {
  Dialog,
  Classes,
  FormGroup,
  InputGroup,
  Button,
  Checkbox,
  Tag,
  Callout,
  HTMLSelect,
} from '@blueprintjs/core'
import { DrillholeData } from '../drillholes/base/DrillHole'
import { useCrossSectionStore } from './CrossSectionStore'

interface CrossSectionCreateDialogProps {
  isOpen: boolean
  onClose: () => void
  data: DrillholeData
}

export const CrossSectionCreateDialog: FC<CrossSectionCreateDialogProps> = ({
  isOpen,
  onClose,
  data,
}) => {
  const {
    setTempStart,
    setTempStop,
    setTempHoles,
    confirmCreation,
    cancelCreation,
  } = useCrossSectionStore()
  
  const [name, setName] = useState('Section 1')
  const [mode, setMode] = useState<'points' | 'holes'>('holes')
  
  const [startE, setStartE] = useState('')
  const [startN, setStartN] = useState('')
  const [stopE, setStopE] = useState('')
  const [stopN, setStopN] = useState('')
  
  const [startHole, setStartHole] = useState('')
  const [stopHole, setStopHole] = useState('')
  
  const [selectedHoles, setSelectedHoles] = useState<Set<string>>(new Set())
  
  const handleConfirm = () => {
    let start: [number, number]
    let stop: [number, number]
    
    if (mode === 'points') {
      start = [parseFloat(startE), parseFloat(startN)]
      stop = [parseFloat(stopE), parseFloat(stopN)]
    } else {
      const startTraj = data.trajectories.find(t => t.hole_id === startHole)
      const stopTraj = data.trajectories.find(t => t.hole_id === stopHole)
      
      if (!startTraj || !stopTraj) return
      
      start = [startTraj.collar.east, startTraj.collar.north]
      stop = [stopTraj.collar.east, stopTraj.collar.north]
    }
    
    setTempStart(start)
    setTempStop(stop)
    setTempHoles(Array.from(selectedHoles))
    confirmCreation(name)
    
    setName('Section 1')
    setSelectedHoles(new Set())
    setStartE('')
    setStartN('')
    setStopE('')
    setStopN('')
    setStartHole('')
    setStopHole('')
    onClose()
  }
  
  const handleCancel = () => {
    cancelCreation()
    setSelectedHoles(new Set())
    setStartE('')
    setStartN('')
    setStopE('')
    setStopN('')
    setStartHole('')
    setStopHole('')
    onClose()
  }
  
  const toggleHole = (holeId: string) => {
    const newSet = new Set(selectedHoles)
    if (newSet.has(holeId)) {
      newSet.delete(holeId)
    } else {
      newSet.add(holeId)
    }
    setSelectedHoles(newSet)
  }
  
  const selectAll = () => {
    setSelectedHoles(new Set(data.trajectories.map(t => t.hole_id)))
  }
  
  const selectNone = () => {
    setSelectedHoles(new Set())
  }
  
  const canConfirm = () => {
    if (mode === 'points') {
      return startE && startN && stopE && stopN && selectedHoles.size > 0
    } else {
      return startHole && stopHole && selectedHoles.size > 0
    }
  }
  
  return (
    <Dialog
      isOpen={isOpen}
      onClose={handleCancel}
      title="Create Cross Section"
      icon="layout"
      className={Classes.DARK}
      style={{ width: '600px', maxHeight: '80vh' }}
    >
      <div className={Classes.DIALOG_BODY}>
        <FormGroup label="Section Name">
          <InputGroup
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Section A-A'"
          />
        </FormGroup>
        
        <FormGroup label="Definition Mode">
          <Button
            text="Points (E, N)"
            active={mode === 'points'}
            onClick={() => setMode('points')}
            style={{ marginRight: '8px' }}
          />
          <Button
            text="Drillholes"
            active={mode === 'holes'}
            onClick={() => setMode('holes')}
          />
        </FormGroup>
        
        {mode === 'points' ? (
          <>
            <FormGroup label="Start Point">
              <div style={{ display: 'flex', gap: '8px' }}>
                <InputGroup
                  placeholder="East"
                  value={startE}
                  onChange={(e) => setStartE(e.target.value)}
                  type="number"
                />
                <InputGroup
                  placeholder="North"
                  value={startN}
                  onChange={(e) => setStartN(e.target.value)}
                  type="number"
                />
              </div>
            </FormGroup>
            
            <FormGroup label="Stop Point">
              <div style={{ display: 'flex', gap: '8px' }}>
                <InputGroup
                  placeholder="East"
                  value={stopE}
                  onChange={(e) => setStopE(e.target.value)}
                  type="number"
                />
                <InputGroup
                  placeholder="North"
                  value={stopN}
                  onChange={(e) => setStopN(e.target.value)}
                  type="number"
                />
              </div>
            </FormGroup>
          </>
        ) : (
          <>
            <FormGroup label="Start Drillhole">
              <HTMLSelect
                value={startHole}
                onChange={(e) => setStartHole(e.target.value)}
                fill
              >
                <option value="">Select...</option>
                {data.trajectories.map(t => (
                  <option key={t.hole_id} value={t.hole_id}>
                    {t.hole_id}
                  </option>
                ))}
              </HTMLSelect>
            </FormGroup>
            
            <FormGroup label="Stop Drillhole">
              <HTMLSelect
                value={stopHole}
                onChange={(e) => setStopHole(e.target.value)}
                fill
              >
                <option value="">Select...</option>
                {data.trajectories.map(t => (
                  <option key={t.hole_id} value={t.hole_id}>
                    {t.hole_id}
                  </option>
                ))}
              </HTMLSelect>
            </FormGroup>
          </>
        )}
        
        <FormGroup
          label={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Drillholes to Include</span>
              <div>
                <Button minimal small text="All" onClick={selectAll} />
                <Button minimal small text="None" onClick={selectNone} />
              </div>
            </div>
          }
        >
          <div style={{ 
            maxHeight: '200px', 
            overflowY: 'auto',
            border: '1px solid #394b59',
            borderRadius: '3px',
            padding: '8px'
          }}>
            {data.trajectories.map(traj => (
              <div 
                key={traj.hole_id}
                style={{ 
                  display: 'flex', 
                  alignItems: 'center',
                  padding: '4px',
                  cursor: 'pointer',
                  borderRadius: '3px'
                }}
                onClick={() => toggleHole(traj.hole_id)}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <Checkbox
                  checked={selectedHoles.has(traj.hole_id)}
                  onChange={() => toggleHole(traj.hole_id)}
                  style={{ margin: 0, marginRight: '8px' }}
                />
                <span style={{ flex: 1 }}>{traj.hole_id}</span>
                <Tag minimal>{traj.collar.max_depth.toFixed(0)}m</Tag>
              </div>
            ))}
          </div>
          <div style={{ marginTop: '8px', fontSize: '12px', color: '#8A9BA8' }}>
            {selectedHoles.size} / {data.trajectories.length} selected
          </div>
        </FormGroup>
        
        <Callout intent="primary" icon="info-sign">
          Selected drillholes will be projected onto the section line.
        </Callout>
      </div>
      
      <div className={Classes.DIALOG_FOOTER}>
        <div className={Classes.DIALOG_FOOTER_ACTIONS}>
          <Button onClick={handleCancel}>Cancel</Button>
          <Button
            intent="primary"
            onClick={handleConfirm}
            disabled={!canConfirm()}
          >
            Create Section
          </Button>
        </div>
      </div>
    </Dialog>
  )
}