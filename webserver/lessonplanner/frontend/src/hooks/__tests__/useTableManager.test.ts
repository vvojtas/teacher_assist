import { describe, it, expect } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useTableManager } from '../useTableManager'

describe('useTableManager', () => {
  describe('initialization', () => {
    it('should initialize with 5 empty rows', () => {
      const { result } = renderHook(() => useTableManager())

      expect(result.current.rows).toHaveLength(5)
      expect(result.current.rows[0]).toMatchObject({
        id: 'row_1',
        module: '',
        curriculum: '',
        objectives: '',
        activity: '',
        aiGenerated: false,
        userEdited: false,
        loading: false,
      })
    })
  })

  describe('addRows', () => {
    it('should add a single row by default', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.addRows()
      })

      expect(result.current.rows).toHaveLength(6)
      expect(result.current.rows[5].id).toBe('row_6')
    })

    it('should add multiple rows when count is specified', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.addRows(3)
      })

      expect(result.current.rows).toHaveLength(8)
      expect(result.current.rows[5].id).toBe('row_6')
      expect(result.current.rows[6].id).toBe('row_7')
      expect(result.current.rows[7].id).toBe('row_8')
    })

    it('should maintain sequential IDs across multiple add operations', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.addRows(2)
      })

      act(() => {
        result.current.addRows(1)
      })

      expect(result.current.rows).toHaveLength(8)
      expect(result.current.rows[7].id).toBe('row_8')
    })

    it('should initialize new rows with empty fields', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.addRows()
      })

      const newRow = result.current.rows[5]
      expect(newRow.module).toBe('')
      expect(newRow.activity).toBe('')
      expect(newRow.aiGenerated).toBe(false)
    })
  })

  describe('deleteRow', () => {
    it('should remove the specified row', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.deleteRow('row_3')
      })

      expect(result.current.rows).toHaveLength(4)
      expect(result.current.rows.find(r => r.id === 'row_3')).toBeUndefined()
    })

    it('should preserve other rows when deleting', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.deleteRow('row_2')
      })

      expect(result.current.rows.find(r => r.id === 'row_1')).toBeDefined()
      expect(result.current.rows.find(r => r.id === 'row_3')).toBeDefined()
    })
  })

  describe('clearAll', () => {
    it('should reset to 5 empty rows', () => {
      const { result } = renderHook(() => useTableManager())

      // Add rows and modify data
      act(() => {
        result.current.addRows(3)
        result.current.updateRow('row_1', { activity: 'Test activity' })
      })

      expect(result.current.rows).toHaveLength(8)

      // Clear all
      act(() => {
        result.current.clearAll()
      })

      expect(result.current.rows).toHaveLength(5)
      expect(result.current.rows[0].activity).toBe('')
    })

    it('should reset row ID counter', () => {
      const { result } = renderHook(() => useTableManager())

      // Add rows, clear, then add again
      act(() => {
        result.current.addRows(5)
      })

      act(() => {
        result.current.clearAll()
      })

      act(() => {
        result.current.addRows()
      })

      // New row should be row_6 (not row_11)
      expect(result.current.rows[5].id).toBe('row_6')
    })
  })

  describe('updateRow', () => {
    it('should update specific fields of a row', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.updateRow('row_1', {
          module: 'Test Module',
          activity: 'Test Activity'
        })
      })

      const updatedRow = result.current.rows.find(r => r.id === 'row_1')
      expect(updatedRow?.module).toBe('Test Module')
      expect(updatedRow?.activity).toBe('Test Activity')
      expect(updatedRow?.curriculum).toBe('') // Unchanged
    })

    it('should not affect other rows', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.updateRow('row_1', { module: 'Updated' })
      })

      expect(result.current.rows.find(r => r.id === 'row_2')?.module).toBe('')
    })

    it('should handle aiGenerated flag updates', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.updateRow('row_1', {
          module: 'AI Module',
          aiGenerated: true
        })
      })

      expect(result.current.rows.find(r => r.id === 'row_1')?.aiGenerated).toBe(true)
    })
  })

  describe('setRowLoading', () => {
    it('should set loading state for specific row', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.setRowLoading('row_1', true)
      })

      expect(result.current.rows.find(r => r.id === 'row_1')?.loading).toBe(true)
      expect(result.current.rows.find(r => r.id === 'row_2')?.loading).toBe(false)
    })

    it('should toggle loading state', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.setRowLoading('row_1', true)
      })

      act(() => {
        result.current.setRowLoading('row_1', false)
      })

      expect(result.current.rows.find(r => r.id === 'row_1')?.loading).toBe(false)
    })
  })

  describe('getRowsNeedingGeneration', () => {
    it('should return rows with activity but no AI data', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.updateRow('row_1', { activity: 'Activity 1' })
        result.current.updateRow('row_2', { activity: 'Activity 2' })
        result.current.updateRow('row_3', { activity: '' }) // No activity
      })

      const needingGeneration = result.current.getRowsNeedingGeneration()
      expect(needingGeneration).toHaveLength(2)
      expect(needingGeneration.map(r => r.id)).toContain('row_1')
      expect(needingGeneration.map(r => r.id)).toContain('row_2')
    })

    it('should exclude rows with AI-generated data', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.updateRow('row_1', {
          activity: 'Activity 1',
          aiGenerated: true,
          module: 'Module'
        })
        result.current.updateRow('row_2', { activity: 'Activity 2' })
      })

      const needingGeneration = result.current.getRowsNeedingGeneration()
      expect(needingGeneration).toHaveLength(1)
      expect(needingGeneration[0].id).toBe('row_2')
    })

    it('should exclude rows with user-edited data', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.updateRow('row_1', {
          activity: 'Activity 1',
          userEdited: true
        })
        result.current.updateRow('row_2', { activity: 'Activity 2' })
      })

      const needingGeneration = result.current.getRowsNeedingGeneration()
      expect(needingGeneration).toHaveLength(1)
      expect(needingGeneration[0].id).toBe('row_2')
    })

    it('should exclude rows with manual data entry', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.updateRow('row_1', {
          activity: 'Activity 1',
          module: 'Manual Module'
        })
        result.current.updateRow('row_2', { activity: 'Activity 2' })
      })

      const needingGeneration = result.current.getRowsNeedingGeneration()
      expect(needingGeneration).toHaveLength(1)
      expect(needingGeneration[0].id).toBe('row_2')
    })
  })

  describe('markUserEdited', () => {
    it('should mark AI-generated row as user-edited', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.updateRow('row_1', { aiGenerated: true })
        result.current.markUserEdited('row_1')
      })

      expect(result.current.rows.find(r => r.id === 'row_1')?.userEdited).toBe(true)
    })

    it('should not mark non-AI rows as user-edited', () => {
      const { result } = renderHook(() => useTableManager())

      act(() => {
        result.current.markUserEdited('row_1')
      })

      expect(result.current.rows.find(r => r.id === 'row_1')?.userEdited).toBe(false)
    })
  })
})
