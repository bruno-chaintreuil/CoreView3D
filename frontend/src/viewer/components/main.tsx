import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { initializeGeo3DObjects } from '../../geo3d/core/Geo3DRegistry'

initializeGeo3DObjects()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
