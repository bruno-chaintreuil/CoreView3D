import { useState } from 'react'
import FileLoader from './components/FileLoader'
import { DrillholeData } from './core/DrillHole'
import './App.css'
import { Viewer } from './components/Viewer'

function App() {
  const [drillholeData, setDrillholeData] = useState<DrillholeData | null>(null)
  const [loading, setLoading] = useState(false)

  const handleDataLoaded = (data: DrillholeData) => {
    setDrillholeData(data)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>CoreView3D</h1>
        <p className="tagline">Open-source 3D Mining Drillhole Viewer</p>
      </header>

      <main className="app-main">
        {!drillholeData ? (
          <div className="upload-section">
            <FileLoader 
              onDataLoaded={handleDataLoaded}
              setLoading={setLoading}
            />
          </div>
        ) : (
          <div className="viewer-section">
            <Viewer data={drillholeData} />
            <button 
              className="reset-button"
              onClick={() => setDrillholeData(null)}
            >
              Load New Data
            </button>
          </div>
        )}

        {loading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <p>Processing drillhole data...</p>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          CoreView3D v0.1.0 | MIT License | 
          <a href="https://github.com/bruno-chaintreuil/CoreView3D" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </p>
      </footer>
    </div>
  )
}

export default App