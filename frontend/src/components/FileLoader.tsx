import { useState, ChangeEvent } from 'react'
import axios from 'axios'
import { DrillholeData } from '../core/DrillHole'

interface FileLoaderProps {
  onDataLoaded: (data: DrillholeData) => void
  setLoading: (loading: boolean) => void
}

export default function FileLoader({ onDataLoaded, setLoading }: FileLoaderProps) {
  const [collarFile, setCollarFile] = useState<File | null>(null)
  const [surveyFile, setSurveyFile] = useState<File | null>(null)
  const [assaysFile, setAssaysFile] = useState<File | null>(null)
  const [error, setError] = useState<string>('')

  const handleFileChange = (
    event: ChangeEvent<HTMLInputElement>,
    setter: (file: File | null) => void
  ) => {
    const file = event.target.files?.[0] || null
    setter(file)
    setError('')
  }

  const handleSubmit = async () => {
    if (!collarFile) {
      setError('Collar file is required')
      return
    }

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('collar_file', collarFile)
      if (surveyFile) {
        formData.append('survey_file', surveyFile)
      }

      const response = await axios.post('/api/process/trajectories', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data.success) {
        let assaysData = undefined
        if (assaysFile) {
          const assaysFormData = new FormData()
          assaysFormData.append('file', assaysFile)
          const assaysResponse = await axios.post('/api/upload/assays', assaysFormData)
          if (assaysResponse.data.success) {
            assaysData = assaysResponse.data.data
          }
        }

        onDataLoaded({
          trajectories: response.data.data,
          assays: assaysData
        })
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error processing files')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="file-Loader">
      <h2>Upload Drillhole Data</h2>
      
      <div className="file-input-group">
        <label>
          <span className="required">Collar CSV *</span>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => handleFileChange(e, setCollarFile)}
          />
          {collarFile && <span className="file-name">✓ {collarFile.name}</span>}
        </label>

        <label>
          <span>Survey CSV (optional)</span>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => handleFileChange(e, setSurveyFile)}
          />
          {surveyFile && <span className="file-name">✓ {surveyFile.name}</span>}
        </label>

        <label>
          <span>Assays CSV (optional)</span>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => handleFileChange(e, setAssaysFile)}
          />
          {assaysFile && <span className="file-name">✓ {assaysFile.name}</span>}
        </label>
      </div>

      {error && <div className="error-message">{error}</div>}

      <button 
        className="upload-button"
        onClick={handleSubmit}
        disabled={!collarFile}
      >
        Process and Visualize
      </button>

      <div className="info-box">
        <h3>Expected CSV Format:</h3>
        <ul>
          <li><strong>Collar:</strong> Hole_ID, East, North, Elevation, Max_Depth, Azimuth, Dip</li>
          <li><strong>Survey:</strong> Hole_ID, Depth, Azimuth, Dip</li>
          <li><strong>Assays:</strong> Hole_ID, From, To, Lithology, [other columns]</li>
        </ul>
        <p>Sample datasets available in the <code>examples/</code> folder</p>
      </div>
    </div>
  )
}
