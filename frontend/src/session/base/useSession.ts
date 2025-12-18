import { useViewerStore } from "../../viewer/base/useViewerStore"
import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { DrillholeData, parseDrillholeData } from '../../drillholes/base/DrillHole'



interface SessionMetadata {
  total_holes: number
  has_survey: boolean
  has_assays: boolean
}

export const useSessionData = (sessionId: string | null) => {
  const [data, setData] = useState<DrillholeData | null>(null)
  const [metadata, setMetadata] = useState<SessionMetadata | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    if (!sessionId) return

    setLoading(true)
    setError(null)

    try {
      const response = await axios.get(`/api/session/load/${sessionId}`)
      
      if (response.data.success) {
        const parsed = parseDrillholeData({
          trajectories: response.data.data.trajectories,
          assays: response.data.data.assays
        })
        parsed.sanitizeData()
        setData(parsed)
        setMetadata(response.data.metadata)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error loading session')
    } finally {
      setLoading(false)
    }
  }, [sessionId])

  const reload = useCallback(() => {
    loadData()
  }, [loadData])

  useEffect(() => {
    loadData()
  }, [loadData])

  return { data, metadata, loading, error, reload }
}

export const useSessionMetadata = (sessionId: string | null) => {
  const [metadata, setMetadata] = useState<SessionMetadata | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sessionId) return

    const fetchMetadata = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await axios.get(`/api/session/metadata/${sessionId}`)
        
        if (response.data.success) {
          setMetadata(response.data.metadata)
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Error loading metadata')
      } finally {
        setLoading(false)
      }
    }

    fetchMetadata()
  }, [sessionId])

  return { metadata, loading, error }
}