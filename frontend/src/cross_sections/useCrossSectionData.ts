import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import { CrossSectionData, CrossSectionDefinition } from '../session/base/useCrossSection'

export const useCrossSectionData = (sessionId: string, definition: CrossSectionDefinition) => {
  const [data, setData] = useState<CrossSectionData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.post('/api/cross-section/calculate', {
        session_id: sessionId,
        ...definition,
      })
      if (response.data.success) setData(response.data)
    } catch (err: any) {
      console.error(err)
      setError(err.response?.data?.detail || err.message || 'Error')
    } finally {
      setLoading(false)
    }
  }, [sessionId, definition])

  useEffect(() => { fetchData() }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}