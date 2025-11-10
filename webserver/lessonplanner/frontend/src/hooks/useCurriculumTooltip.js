import { useState, useCallback, useRef } from 'react'

/**
 * Custom hook for fetching and caching curriculum reference tooltips
 */
export function useCurriculumTooltip() {
  const [tooltipCache] = useState(new Map())
  const TOOLTIP_TIMEOUT = 10000 // 10 seconds

  /**
   * Fetch curriculum reference text for tooltip
   */
  const fetchCurriculumText = useCallback(async (code) => {
    // Check cache first
    if (tooltipCache.has(code)) {
      return tooltipCache.get(code)
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), TOOLTIP_TIMEOUT)

    try {
      const response = await fetch(`/api/curriculum-refs/${code}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Nie znaleziono opisu')
      }

      // Cache the result
      tooltipCache.set(code, data.full_text)

      return data.full_text

    } catch (error) {
      clearTimeout(timeoutId)
      if (error.name === 'AbortError') {
        console.error('Tooltip fetch timeout:', code)
        return 'Przekroczono limit czasu pobierania opisu'
      }
      console.error('Error fetching tooltip:', error)
      return `Nie znaleziono opisu dla kodu: ${code}`
    }
  }, [tooltipCache])

  /**
   * Parse curriculum codes from text (e.g., "4.15, 4.18" -> ["4.15", "4.18"])
   */
  const parseCurriculumCodes = useCallback((text) => {
    if (!text) return []
    const codePattern = /\d+\.\d+/g
    return text.match(codePattern) || []
  }, [])

  /**
   * Fetch tooltip texts for multiple codes
   */
  const fetchMultipleCodes = useCallback(async (codes) => {
    const results = await Promise.all(
      codes.map(code => fetchCurriculumText(code))
    )

    return codes.map((code, index) => ({
      code,
      text: results[index]
    }))
  }, [fetchCurriculumText])

  return {
    fetchCurriculumText,
    parseCurriculumCodes,
    fetchMultipleCodes
  }
}
