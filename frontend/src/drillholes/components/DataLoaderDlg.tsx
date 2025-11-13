import { FC, useState } from 'react'
import {
  Dialog,
  Classes,
  FileInput,
  Button,
  FormGroup,
  Callout,
  Spinner
} from '@blueprintjs/core'
import axios from 'axios'
import { DrillholeData, parseDrillholeData } from '../base/DrillHole'

interface DataLoaderDialogProps {
  isOpen: boolean
  onClose: () => void
  onDataLoaded: (data: DrillholeData) => void
}

type UploadMode = 'csv' | 'excel'

export const DataLoaderDialog: FC<DataLoaderDialogProps> = ({
  isOpen,
  onClose,
  onDataLoaded
}) => {
  const [mode, setMode] = useState<UploadMode>('csv')
  const [collarFile, setCollarFile] = useState<File | null>(null)
  const [surveyFile, setSurveyFile] = useState<File | null>(null)
  const [assaysFile, setAssaysFile] = useState<File | null>(null)
  const [excelFile, setExcelFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFileChange = (
    e: React.FormEvent<HTMLInputElement>,
    setter: (file: File | null) => void
  ) => {
    const target = e.currentTarget as HTMLInputElement
    const file = target.files?.[0] || null
    setter(file)
  }

  const handleSubmit = async () => {
    setError('')
    setLoading(true)

    try {
      let response
      let assaysData = undefined

      if (mode === 'csv') {
        if (!collarFile) throw new Error('Collar file is required')

        const formData = new FormData()
        formData.append('collar_file', collarFile)
        if (surveyFile) formData.append('survey_file', surveyFile)

        response = await axios.post('/api/process/trajectories', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        if (assaysFile) {
          const assaysFormData = new FormData()
          assaysFormData.append('file', assaysFile)
          const assaysResponse = await axios.post('/api/upload/assays', assaysFormData)
          if (assaysResponse.data.success) assaysData = assaysResponse.data.data
        }
      } else {
        if (!excelFile) throw new Error('Excel file is required')
        const formData = new FormData()
        formData.append('file', excelFile)

        response = await axios.post('/api/process/excel-trajectories', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      }

      if (response.data.success) {
        const parsed = parseDrillholeData({
          trajectories: response.data.data.trajectories ?? response.data.data,
          assays: assaysData
        })
        parsed.sanitizeData()
        onDataLoaded(parsed)
        onClose()
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error processing data')
    } finally {
      setLoading(false)
    }
  }

  const canSubmit = mode === 'csv' ? !!collarFile : !!excelFile

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title="Load Drillhole Data"
      icon="folder-open"
      className={Classes.DARK}
      style={{ width: '600px' }}
      canOutsideClickClose={false}
    >
      <div className={Classes.DIALOG_BODY}>
        <FormGroup label="Data Format">
          <Button
            text="CSV Files"
            icon="document"
            active={mode === 'csv'}
            onClick={() => setMode('csv')}
            style={{ marginRight: '8px' }}
          />
          <Button
            text="Excel File"
            icon="th"
            active={mode === 'excel'}
            onClick={() => setMode('excel')}
          />
        </FormGroup>

        {mode === 'csv' ? (
          <>
            <FormGroup
              label="Collar CSV"
              labelInfo="(required)"
              helperText="Contains drillhole locations and orientations"
            >
              <FileInput
                text={collarFile?.name || 'Choose file...'}
                onInputChange={(e) => handleFileChange(e, setCollarFile)}
                inputProps={{ accept: '.csv' }}
                fill
              />
            </FormGroup>

            <FormGroup
              label="Survey CSV"
              labelInfo="(optional)"
              helperText="Contains deviation measurements"
            >
              <FileInput
                text={surveyFile?.name || 'Choose file...'}
                onInputChange={(e) => handleFileChange(e, setSurveyFile)}
                inputProps={{ accept: '.csv' }}
                fill
              />
            </FormGroup>

            <FormGroup
              label="Assays CSV"
              labelInfo="(optional)"
              helperText="Contains lithology and geochemistry"
            >
              <FileInput
                text={assaysFile?.name || 'Choose file...'}
                onInputChange={(e) => handleFileChange(e, setAssaysFile)}
                inputProps={{ accept: '.csv' }}
                fill
              />
            </FormGroup>

            <Callout intent="primary" icon="info-sign">
              <strong>Expected columns:</strong>
              <ul style={{ marginTop: '8px', marginBottom: 0 }}>
                <li>Collar: Hole_ID, East, North, Elevation, Max_Depth, Azimuth, Dip</li>
                <li>Survey: Hole_ID, Depth, Azimuth, Dip</li>
                <li>Assays: Hole_ID, From, To, Lithology, [grades]</li>
              </ul>
            </Callout>
          </>
        ) : (
          <>
            <FormGroup
              label="Excel File (.xlsx)"
              labelInfo="(required)"
              helperText="Must contain 'Collar' sheet, optional 'Survey' and 'Assays' sheets"
            >
              <FileInput
                text={excelFile?.name || 'Choose file...'}
                onInputChange={(e) => handleFileChange(e, setExcelFile)}
                inputProps={{ accept: '.xlsx' }}
                fill
              />
            </FormGroup>

            <Callout intent="primary" icon="info-sign">
              <strong>Excel structure:</strong>
              <ul style={{ marginTop: '8px', marginBottom: 0 }}>
                <li>Sheet "Collar": Required (same columns as CSV)</li>
                <li>Sheet "Survey": Optional (deviation data)</li>
                <li>Sheet "Assays": Optional (lithology & grades)</li>
              </ul>
            </Callout>
          </>
        )}

        {error && (
          <Callout intent="danger" icon="error" style={{ marginTop: '16px' }}>
            {error}
          </Callout>
        )}
      </div>

      <div className={Classes.DIALOG_FOOTER}>
        <div className={Classes.DIALOG_FOOTER_ACTIONS}>
          <Button onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            intent="primary"
            onClick={handleSubmit}
            disabled={!canSubmit || loading}
            icon={loading ? <Spinner size={16} /> : 'upload'}
          >
            {loading ? 'Processing...' : 'Load Data'}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}
