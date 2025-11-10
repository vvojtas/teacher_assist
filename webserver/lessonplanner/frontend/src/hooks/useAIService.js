import { useCallback, useRef } from 'react'

/**
 * Custom hook for AI service API calls
 * Replaces the AIService singleton from vanilla JS
 */
export function useAIService() {
  const REQUEST_TIMEOUT = 120000 // 120 seconds

  /**
   * Get CSRF token from cookies for Django requests
   */
  const getCsrfToken = useCallback(() => {
    const name = 'csrftoken'
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';')
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim()
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
          break
        }
      }
    }
    return cookieValue
  }, [])

  /**
   * Get user-friendly error message based on error type
   */
  const getUserFriendlyErrorMessage = useCallback((error) => {
    if (error.name === 'AbortError') {
      return 'Żądanie przekroczyło limit czasu (120s). Spróbuj ponownie.'
    } else if (error.message?.includes('fetch') || error.message?.includes('NetworkError')) {
      return 'Nie można połączyć z usługą AI. Sprawdź połączenie internetowe.'
    } else {
      return error.message || 'Wystąpił nieoczekiwany błąd.'
    }
  }, [])

  /**
   * Generate metadata for a single activity
   */
  const generateSingle = useCallback(async (activity, theme = '') => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT)

    try {
      const response = await fetch('/api/fill-work-plan/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
          activity: activity,
          theme: theme
        }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Błąd serwera')
      }

      return {
        module: data.module,
        curriculum: Array.isArray(data.curriculum_refs)
          ? data.curriculum_refs.join(', ')
          : data.curriculum_refs,
        objectives: Array.isArray(data.objectives)
          ? data.objectives.join('\n')
          : data.objectives,
        aiGenerated: true,
        userEdited: false
      }

    } catch (error) {
      clearTimeout(timeoutId)
      console.error('Error generating metadata:', error)
      throw new Error(getUserFriendlyErrorMessage(error))
    }
  }, [getCsrfToken, getUserFriendlyErrorMessage])

  /**
   * Generate metadata for multiple rows (sequential)
   */
  const generateBulk = useCallback(async (rows, theme, onProgress) => {
    const results = {
      succeeded: 0,
      failed: [],
      total: rows.length
    }

    for (let i = 0; i < rows.length; i++) {
      const row = rows[i]

      try {
        const data = await generateSingle(row.activity, theme)
        results.succeeded++

        // Call progress callback
        if (onProgress) {
          onProgress({
            rowId: row.id,
            success: true,
            data,
            completed: i + 1,
            total: rows.length
          })
        }
      } catch (error) {
        results.failed.push({
          rowId: row.id,
          activity: row.activity,
          error: error.message
        })

        // Call progress callback with error
        if (onProgress) {
          onProgress({
            rowId: row.id,
            success: false,
            error: error.message,
            completed: i + 1,
            total: rows.length
          })
        }
      }
    }

    return results
  }, [generateSingle])

  return {
    generateSingle,
    generateBulk,
    getUserFriendlyErrorMessage
  }
}
