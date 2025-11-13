import { describe, it, expect, beforeEach, vi, beforeAll } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useAIService } from '../useAIService'

describe('useAIService', () => {
  beforeAll(() => {
    // Mock fetch globally
    global.fetch = vi.fn()
  })

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock CSRF token in cookie - only after document is available
    if (typeof document !== 'undefined') {
      Object.defineProperty(document, 'cookie', {
        writable: true,
        value: 'csrftoken=test-csrf-token',
      })
    }
  })

  describe('generateSingle', () => {
    it('should successfully generate metadata for activity', async () => {
      const mockResponse = {
        module: 'Test Module',
        curriculum_refs: ['REF1', 'REF2'],
        objectives: ['Objective 1', 'Objective 2'],
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => mockResponse,
      })

      const { result } = renderHook(() => useAIService())

      const data = await result.current.generateSingle('Test activity', 'Test theme')

      expect(data).toEqual({
        module: 'Test Module',
        curriculum: 'REF1, REF2',
        objectives: 'Objective 1\nObjective 2',
        aiGenerated: true,
        userEdited: false,
      })

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/fill-work-plan/',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test-csrf-token',
          }),
          body: JSON.stringify({
            activity: 'Test activity',
            theme: 'Test theme',
          }),
        })
      )
    })

    it('should throw error when CSRF token is missing', async () => {
      if (typeof document !== 'undefined') {
        // Clear cookie
        Object.defineProperty(document, 'cookie', {
          writable: true,
          value: '',
        })

        // Remove meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]')
        if (metaTag) metaTag.remove()
      }

      const { result } = renderHook(() => useAIService())

      await expect(
        result.current.generateSingle('Test activity')
      ).rejects.toThrow('Brak tokenu CSRF')
    })

    it('should handle non-JSON responses (CSRF error)', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 403,
        headers: new Headers({ 'content-type': 'text/html' }),
        text: async () => '<html>Forbidden</html>',
      })

      const { result } = renderHook(() => useAIService())

      await expect(
        result.current.generateSingle('Test activity')
      ).rejects.toThrow('Błąd CSRF')
    })

    it('should handle server errors', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ error: 'Internal server error' }),
      })

      const { result } = renderHook(() => useAIService())

      await expect(
        result.current.generateSingle('Test activity')
      ).rejects.toThrow('Internal server error')
    })

    it('should handle network errors', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useAIService())

      await expect(
        result.current.generateSingle('Test activity')
      ).rejects.toThrow('Nie można połączyć z usługą AI')
    })

    it('should handle timeout (abort)', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(
        Object.assign(new Error('The operation was aborted'), { name: 'AbortError' })
      )

      const { result } = renderHook(() => useAIService())

      await expect(
        result.current.generateSingle('Test activity')
      ).rejects.toThrow('przekroczyło limit czasu')
    })

    it('should handle curriculum refs as string', async () => {
      const mockResponse = {
        module: 'Test Module',
        curriculum_refs: 'REF1, REF2, REF3',
        objectives: 'Single objective',
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => mockResponse,
      })

      const { result } = renderHook(() => useAIService())

      const data = await result.current.generateSingle('Test activity')

      expect(data.curriculum).toBe('REF1, REF2, REF3')
      expect(data.objectives).toBe('Single objective')
    })

    it('should use empty theme by default', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ module: 'M', curriculum_refs: [], objectives: [] }),
      })

      const { result } = renderHook(() => useAIService())

      await result.current.generateSingle('Test activity')

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: expect.stringContaining('"theme":""'),
        })
      )
    })
  })

  describe('generateBulk', () => {
    it('should process multiple rows sequentially', async () => {
      const mockRows = [
        { id: 'row_1', activity: 'Activity 1', module: '', curriculum: '', objectives: '', aiGenerated: false, userEdited: false, loading: false },
        { id: 'row_2', activity: 'Activity 2', module: '', curriculum: '', objectives: '', aiGenerated: false, userEdited: false, loading: false },
      ]

      ;(global.fetch as any).mockResolvedValue({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({
          module: 'Module',
          curriculum_refs: [],
          objectives: [],
        }),
      })

      const { result } = renderHook(() => useAIService())
      const progressCallback = vi.fn()

      const results = await result.current.generateBulk(mockRows, 'Theme', progressCallback)

      expect(results.succeeded).toBe(2)
      expect(results.failed).toHaveLength(0)
      expect(results.total).toBe(2)
      expect(progressCallback).toHaveBeenCalledTimes(2)
      expect(global.fetch).toHaveBeenCalledTimes(2)
    })

    it('should call progress callback with success data', async () => {
      const mockRows = [
        { id: 'row_1', activity: 'Activity 1', module: '', curriculum: '', objectives: '', aiGenerated: false, userEdited: false, loading: false },
      ]

      const mockResponseData = {
        module: 'Test Module',
        curriculum_refs: ['REF1'],
        objectives: ['Objective 1'],
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => mockResponseData,
      })

      const { result } = renderHook(() => useAIService())
      const progressCallback = vi.fn()

      await result.current.generateBulk(mockRows, 'Theme', progressCallback)

      expect(progressCallback).toHaveBeenCalledWith({
        rowId: 'row_1',
        success: true,
        data: expect.objectContaining({
          module: 'Test Module',
          aiGenerated: true,
        }),
        completed: 1,
        total: 1,
      })
    })

    it('should handle partial failures', async () => {
      const mockRows = [
        { id: 'row_1', activity: 'Activity 1', module: '', curriculum: '', objectives: '', aiGenerated: false, userEdited: false, loading: false },
        { id: 'row_2', activity: 'Activity 2', module: '', curriculum: '', objectives: '', aiGenerated: false, userEdited: false, loading: false },
        { id: 'row_3', activity: 'Activity 3', module: '', curriculum: '', objectives: '', aiGenerated: false, userEdited: false, loading: false },
      ]

      ;(global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => ({ module: 'M', curriculum_refs: [], objectives: [] }),
        })
        .mockRejectedValueOnce(new Error('API Error'))
        .mockResolvedValueOnce({
          ok: true,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => ({ module: 'M', curriculum_refs: [], objectives: [] }),
        })

      const { result } = renderHook(() => useAIService())
      const progressCallback = vi.fn()

      const results = await result.current.generateBulk(mockRows, 'Theme', progressCallback)

      expect(results.succeeded).toBe(2)
      expect(results.failed).toHaveLength(1)
      expect(results.failed[0]).toMatchObject({
        rowId: 'row_2',
        activity: 'Activity 2',
        error: expect.stringContaining('API Error'),
      })
    })

    it('should call progress callback for failures', async () => {
      const mockRows = [
        { id: 'row_1', activity: 'Activity 1', module: '', curriculum: '', objectives: '', aiGenerated: false, userEdited: false, loading: false },
      ]

      ;(global.fetch as any).mockRejectedValueOnce(new Error('Test error'))

      const { result } = renderHook(() => useAIService())
      const progressCallback = vi.fn()

      await result.current.generateBulk(mockRows, 'Theme', progressCallback)

      expect(progressCallback).toHaveBeenCalledWith({
        rowId: 'row_1',
        success: false,
        error: expect.stringContaining('error'),
        completed: 1,
        total: 1,
      })
    })

    it('should work without progress callback', async () => {
      const mockRows = [
        { id: 'row_1', activity: 'Activity 1', module: '', curriculum: '', objectives: '', aiGenerated: false, userEdited: false, loading: false },
      ]

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ module: 'M', curriculum_refs: [], objectives: [] }),
      })

      const { result } = renderHook(() => useAIService())

      const results = await result.current.generateBulk(mockRows, 'Theme')

      expect(results.succeeded).toBe(1)
    })
  })

  describe('getUserFriendlyErrorMessage', () => {
    it('should return timeout message for AbortError', () => {
      const { result } = renderHook(() => useAIService())

      const error = Object.assign(new Error('Aborted'), { name: 'AbortError' })
      const message = result.current.getUserFriendlyErrorMessage(error)

      expect(message).toContain('limit czasu')
    })

    it('should return network error message', () => {
      const { result } = renderHook(() => useAIService())

      const error = new Error('Failed to fetch')
      const message = result.current.getUserFriendlyErrorMessage(error)

      expect(message).toContain('połączyć z usługą AI')
    })

    it('should return original message for other errors', () => {
      const { result } = renderHook(() => useAIService())

      const error = new Error('Custom error message')
      const message = result.current.getUserFriendlyErrorMessage(error)

      expect(message).toBe('Custom error message')
    })
  })
})
