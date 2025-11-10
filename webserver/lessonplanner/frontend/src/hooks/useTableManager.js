import { useState, useCallback } from 'react'

/**
 * Custom hook for managing table rows and their state
 * Replaces the TableManager singleton from vanilla JS
 */
export function useTableManager() {
  const [rows, setRows] = useState(() => {
    // Initialize with 5 empty rows
    return Array.from({ length: 5 }, (_, i) => ({
      id: `row_${i + 1}`,
      module: '',
      curriculum: '',
      objectives: '',
      activity: '',
      aiGenerated: false,
      userEdited: false,
      loading: false,
    }))
  })

  const [nextRowId, setNextRowId] = useState(6)

  /**
   * Add a specified number of empty rows
   */
  const addRows = useCallback((count = 1) => {
    setRows(prev => {
      const newRows = Array.from({ length: count }, (_, i) => ({
        id: `row_${nextRowId + i}`,
        module: '',
        curriculum: '',
        objectives: '',
        activity: '',
        aiGenerated: false,
        userEdited: false,
        loading: false,
      }))
      setNextRowId(nextRowId + count)
      return [...prev, ...newRows]
    })
  }, [nextRowId])

  /**
   * Delete a specific row
   */
  const deleteRow = useCallback((rowId) => {
    setRows(prev => prev.filter(row => row.id !== rowId))
  }, [])

  /**
   * Clear all rows and reset to 5 empty rows
   */
  const clearAll = useCallback(() => {
    setRows(Array.from({ length: 5 }, (_, i) => ({
      id: `row_${i + 1}`,
      module: '',
      curriculum: '',
      objectives: '',
      activity: '',
      aiGenerated: false,
      userEdited: false,
      loading: false,
    })))
    setNextRowId(6)
  }, [])

  /**
   * Update a specific row's data
   */
  const updateRow = useCallback((rowId, updates) => {
    setRows(prev => prev.map(row =>
      row.id === rowId ? { ...row, ...updates } : row
    ))
  }, [])

  /**
   * Set row loading state
   */
  const setRowLoading = useCallback((rowId, loading) => {
    setRows(prev => prev.map(row =>
      row.id === rowId ? { ...row, loading } : row
    ))
  }, [])

  /**
   * Get rows that need AI generation (have activity but no AI data or user edits)
   */
  const getRowsNeedingGeneration = useCallback(() => {
    return rows.filter(row =>
      row.activity &&
      !row.aiGenerated &&
      !row.userEdited &&
      !row.module &&
      !row.curriculum &&
      !row.objectives
    )
  }, [rows])

  /**
   * Mark that user has edited a row (for regenerate confirmation)
   */
  const markUserEdited = useCallback((rowId) => {
    setRows(prev => prev.map(row =>
      row.id === rowId && row.aiGenerated
        ? { ...row, userEdited: true }
        : row
    ))
  }, [])

  return {
    rows,
    addRows,
    deleteRow,
    clearAll,
    updateRow,
    setRowLoading,
    getRowsNeedingGeneration,
    markUserEdited,
  }
}
