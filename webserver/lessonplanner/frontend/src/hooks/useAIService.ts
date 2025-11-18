import { useCallback } from 'react'
import type { Row } from './useTableManager'

// Request timeout for AI generation API calls (milliseconds)
const REQUEST_TIMEOUT_MS = 120000 // 120 seconds

export interface GenerateResult {
  module: string
  curriculum: string
  objectives: string
  aiGenerated: boolean
  userEdited: boolean
}

export interface ProgressCallback {
  rowId: string
  success: boolean
  data?: GenerateResult
  error?: string
  completed: number
  total: number
}

export interface BulkResult {
  succeeded: number
  failed: Array<{
    rowId: string
    activity: string
    error: string
  }>
  total: number
}

/**
 * Custom hook for AI service API calls
 * Replaces the AIService singleton from vanilla JS
 */
export function useAIService() {
  /**
   * Get CSRF token from cookies or meta tag for Django requests
   */
  const getCsrfToken = useCallback((): string | null => {
    // Try to get from cookie first (Django default)
    const name = 'csrftoken'
    let cookieValue: string | null = null
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';')
      for (const rawCookie of cookies) {
        const cookie = rawCookie.trim()
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
          break
        }
      }
    }

    // Fallback to meta tag if cookie not found
    if (!cookieValue) {
      const metaTag = document.querySelector('meta[name="csrf-token"]')
      if (metaTag) {
        cookieValue = metaTag.getAttribute('content')
      }
    }

    // Debug logging
    if (!cookieValue) {
      console.warn('CSRF token not found in cookie or meta tag')
    }

    return cookieValue
  }, [])

  /**
   * Get user-friendly error message based on error type
   */
  const getUserFriendlyErrorMessage = useCallback((error: Error): string => {
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
  const generateSingle = useCallback(async (activity: string, theme = ''): Promise<GenerateResult> => {
    // Validate CSRF token exists before making request
    const csrfToken = getCsrfToken()
    if (!csrfToken) {
      throw new Error('Brak tokenu CSRF. Odśwież stronę i spróbuj ponownie.')
    }

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

    try {
      const response = await fetch('/api/fill-work-plan/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          activity: activity,
          theme: theme
        }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      // Check if response is JSON before parsing
      const contentType = response.headers.get('content-type')
      if (!contentType?.includes('application/json')) {
        // Django returned HTML error page (likely CSRF failure)
        const text = await response.text()
        console.error('Non-JSON response:', text.substring(0, 500))

        if (response.status === 403) {
          throw new Error('Błąd CSRF - odśwież stronę i spróbuj ponownie.')
        }
        throw new Error(`Błąd serwera (${response.status}): Nieprawidłowy format odpowiedzi`)
      }

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
      throw new Error(getUserFriendlyErrorMessage(error as Error))
    }
  }, [getCsrfToken, getUserFriendlyErrorMessage])

  /**
   * Generate metadata for multiple rows (sequential)
   */
  const generateBulk = useCallback(async (
    rows: Row[],
    theme: string,
    onProgress?: (progress: ProgressCallback) => void
  ): Promise<BulkResult> => {
    const results: BulkResult = {
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
          error: (error as Error).message
        })

        // Call progress callback with error
        if (onProgress) {
          onProgress({
            rowId: row.id,
            success: false,
            error: (error as Error).message,
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
