import { FC, useState } from 'react'
import { 
  Navbar, 
  NavbarGroup, 
  NavbarHeading,
  NavbarDivider,
  Button,
  Menu,
  MenuItem,
  MenuDivider,
  Alignment,
  Classes,
  Slider
} from '@blueprintjs/core'
import { Popover2 } from '@blueprintjs/popover2'
import '@blueprintjs/popover2/lib/css/blueprint-popover2.css'
import { useViewerStore } from '../base/useViewerStore'

export type CameraView = 'top' | 'front' | 'side' | 'iso' | 'reset'

interface MenuBarProps {
  sessionId?: string,
  onOpenLoader: () => void
  onExportScreenshot: () => void
  onSaveSession?: () => void
  onExportSession?: () => void
  onImportSession?: (file: File) => void
  onClearSession?: () => void
  showCrossSection?: boolean
  onOpenCrossSection?: () => void
}

export const MenuBar: FC<MenuBarProps> = ({ 
  onOpenLoader,
  onExportScreenshot,
  onSaveSession,
  onExportSession,
  onImportSession,
  onClearSession,
  onOpenCrossSection,
  sessionId,
}) => {
  const { setCameraView, showDataTree, setShowDataTree, zScale, setZScale } = useViewerStore()
  const selectedHoleIds = useViewerStore(s => s.selectedHoleIds);
  
  const handleExportScreenshot = () => {
    onExportScreenshot()
  }

  const handleOpenGitHub = () => {
    window.open('https://github.com/bruno-chaintreuil/CoreView3D', '_blank')
  }

  const handleToggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
    handleToggleFullscreen?.()
  }

  const handleImportSession = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file && onImportSession) {
        onImportSession(file)
      }
    }
    input.click()
  }

  const analysisMenu = (
    <Menu className={Classes.DARK}>
      <MenuItem 
        icon="horizontal-distribution" 
        text="Cross-Section" 
        onClick={onOpenCrossSection}
        disabled={!sessionId}
      />
      <MenuItem icon="grid-view" text="Block Model" disabled />
      <MenuItem icon="scatter-plot" text="Interpolation" disabled />
    </Menu>
  )

  const fileMenu = (
    <Menu className={Classes.DARK}>
      <MenuItem 
        icon="folder-open" 
        text="Open Data..." 
        onClick={onOpenLoader}
        labelElement={<span style={{ opacity: 0.5 }}>Ctrl+O</span>}
      />
      <MenuDivider title="Session" />
      <MenuItem 
        icon="floppy-disk" 
        text="Save Session" 
        onClick={onSaveSession}
        disabled={!onSaveSession}
        labelElement={<span style={{ opacity: 0.5 }}>Ctrl+S</span>}
      />
      <MenuItem 
        icon="export" 
        text="Export Session..." 
        onClick={onExportSession}
        disabled={!onExportSession}
      />
      <MenuItem 
        icon="import" 
        text="Import Session..." 
        onClick={handleImportSession}
        disabled={!onImportSession}
      />
      <MenuItem 
        icon="trash" 
        text="Clear Session" 
        onClick={onClearSession}
        disabled={!onClearSession}
        intent="danger"
      />
      <MenuDivider />
      <MenuItem 
        icon="cog" 
        text="Cross-sections" 
        onClick={onOpenCrossSection}
      />
      <MenuDivider />
      <MenuItem 
        icon="camera" 
        text="Export Screenshot" 
        onClick={handleExportScreenshot}
      />
      <MenuDivider />
      <MenuItem 
        icon="cog" 
        text="Settings" 
        disabled
      />
    </Menu>
  )

  const viewMenu = (
    <Menu className={Classes.DARK}>
      <MenuItem 
        icon="panel-table" 
        text="Data Tree" 
        onClick={()=> setShowDataTree(!showDataTree)}
        label={showDataTree ? "✓" : ""}
        labelElement={<span style={{ opacity: 0.5 }}>Ctrl+T</span>}
      />
      <MenuItem 
        icon="fullscreen" 
        text="Fullscreen" 
        onClick={handleToggleFullscreen}
        labelElement={<span style={{ opacity: 0.5 }}>F11</span>}
      />
      <MenuDivider title="Camera Views" />
      <MenuItem 
        icon="symbol-square" 
        text="Top View" 
        onClick={() => setCameraView('top')}
        labelElement={<span style={{ opacity: 0.5 }}>1</span>}
      />
      <MenuItem 
        icon="symbol-square" 
        text="Front View" 
        onClick={() => setCameraView('front')}
        labelElement={<span style={{ opacity: 0.5 }}>2</span>}
      />
      <MenuItem 
        icon="symbol-square" 
        text="Side View" 
        onClick={() => setCameraView('side')}
        labelElement={<span style={{ opacity: 0.5 }}>3</span>}
      />
      <MenuItem 
        icon="cube" 
        text="Isometric" 
        onClick={() => setCameraView('iso')}
        labelElement={<span style={{ opacity: 0.5 }}>4</span>}
      />
      <MenuDivider />
      <MenuItem 
        icon="refresh" 
        text="Reset Camera" 
        onClick={() => setCameraView('reset')}
        labelElement={<span style={{ opacity: 0.5 }}>R</span>}
      />
    </Menu>
  )

  const helpMenu = (
    <Menu className={Classes.DARK}>
      <MenuItem 
        icon="help" 
        text="Documentation" 
        disabled
      />
      <MenuItem 
        icon="info-sign" 
        text="About CoreView3D" 
        disabled
      />
      <MenuDivider />
      <MenuItem 
        icon="code" 
        text="GitHub Repository" 
        onClick={handleOpenGitHub}
      />
      <MenuItem 
        icon="issue" 
        text="Report Issue" 
        onClick={() => window.open('https://github.com/bruno-chaintreuil/CoreView3D/issues', '_blank')}
      />
    </Menu>
  )

  return (
    <Navbar className={Classes.DARK} style={{ background: '#1C2127', height: '40px' }}>
      <NavbarGroup align={Alignment.LEFT}>
        <NavbarHeading>
          <span style={{ fontWeight: 600, fontSize: '14px' }}>CoreView3D</span>
        </NavbarHeading>
        <NavbarDivider />
        
        <Popover2 content={fileMenu} placement="bottom-start">
          <Button className={Classes.MINIMAL} text="File" small />
        </Popover2>
        
        <Popover2 content={viewMenu} placement="bottom-start">
          <Button className={Classes.MINIMAL} text="View" small />
        </Popover2>
        
        <Popover2 content={helpMenu} placement="bottom-start">
          <Button className={Classes.MINIMAL} text="Help" small />
        </Popover2>
      </NavbarGroup>

      <NavbarGroup align={Alignment.RIGHT}>
        <Button
          icon="layout"
          text="cross-section"
          disabled={selectedHoleIds.length < 1}
          onClick={onOpenCrossSection}
        />
        <Slider
          min={0.1}
          max={5}
          stepSize={0.1}
          labelStepSize={2.5}
          value={zScale}
          onChange={setZScale}
          vertical={false}
        />
        <NavbarDivider />
        <Button 
          className={Classes.MINIMAL} 
          icon="camera" 
          title="Export Screenshot"
          onClick={handleExportScreenshot}
          small
        />
        <NavbarDivider />
        <Button 
          className={Classes.MINIMAL} 
          icon="cog" 
          title="Settings" 
          disabled
          small
        />
      </NavbarGroup>
    </Navbar>
  )
}